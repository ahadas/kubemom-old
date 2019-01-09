# Memory Overcommitment Manager
# Copyright (C) 2010 Adam Litke, IBM Corporation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from mom.Collectors.Collector import *
from prometheus_client.parser import text_string_to_metric_families
import requests
import logging

class NodeExporter(Collector):
    """
    This Collctor returns memory statistics about the host by Node Exporter via
    a prometheus endpoint.  The fields provided are:
        mem_available - The total amount of available memory (kB)
        mem_unused    - The amount of memory that is not being used for any purpose (kB)
        mem_free      - The amount of free memory including some caches (kB)
        swap_in       - The amount of memory swapped in since the last collection (pages)
        swap_out      - The amount of memory swapped out since the last collection (pages)
        anon_pages    - The amount of memory used for anonymous memory areas (kB)
    """
    def __init__(self, properties):
        self._logger = logging.getLogger('mom.NodeExporter')
        self._logger.info('initialized')
        self.swap_in_prev = None
        self.swap_in_cur = None
        self.swap_out_prev = None
        self.swap_out_cur = None
        self.meminfo_fields = [
            'node_memory_MemTotal_bytes',
            'node_memory_AnonPages_bytes',
            'node_memory_MemFree_bytes',
            'node_memory_Buffers_bytes',
            'node_memory_Cached_bytes',
            'node_memory_SwapTotal_bytes',
            'node_memory_SwapFree_bytes',
        ]
        self.vmstat_fields = {
            'node_vmstat_pswpin',
            'node_vmstat_pswpout',
        }

    def __del__(self):
        pass

    def collect(self):
        text_string = requests.get("http://127.0.0.1:9101/metrics").text
        metrics = {}
        for family in text_string_to_metric_families(text_string):
            if family.name in self.meminfo_fields:
                label = family.name
                metrics[label] = int(family.samples[0].value) / 1024
                continue

            if family.name in self.vmstat_fields:
                label = family.name
                metrics[label] = int(family.samples[0].value)
                continue
        
        # /proc/vmstat reports cumulative statistics so we must subtract the
        # previous values to get the difference since the last collection.
        self.swap_in_prev = self.swap_in_cur
        self.swap_out_prev = self.swap_out_cur
        self.swap_in_cur = metrics['node_vmstat_pswpin']
        self.swap_out_cur = metrics['node_vmstat_pswpout']
        if self.swap_in_prev is None:
            self.swap_in_prev = self.swap_in_cur
        if self.swap_out_prev is None:
            self.swap_out_prev = self.swap_out_cur
        swap_in = self.swap_in_cur - self.swap_in_prev
        swap_out = self.swap_out_cur - self.swap_out_prev

        swap_usage = metrics['node_memory_SwapTotal_bytes'] - \
            metrics['node_memory_SwapFree_bytes']

        free = metrics['node_memory_MemFree_bytes'] + \
            metrics['node_memory_Buffers_bytes'] + \
            metrics['node_memory_Cached_bytes']

        data = {
            'mem_available': metrics['node_memory_MemTotal_bytes'],
            'mem_unused':    metrics['node_memory_MemFree_bytes'],
            'mem_free':      free,
            'swap_in':       swap_in,
            'swap_out':      swap_out,
            'anon_pages':    metrics['node_memory_AnonPages_bytes'],
            'swap_total':    metrics['node_memory_SwapTotal_bytes'],
            'swap_usage':    swap_usage
        }

        self._logger.info(data)
        return data

    def getFields(self=None):
        return set(['mem_available', 'mem_unused', 'mem_free', 'swap_in', \
                   'swap_out', 'anon_pages', 'swap_total', 'swap_usage'])