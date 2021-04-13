# Python std library imports
from enum import Enum
from typing import Dict
import json
import os

# 3rd-party imports
from nats_bench.api_size import NATSsize
from nats_bench.api_size import ALL_BASE_NAMES as sss_base_names
from nats_bench.api_topology import NATStopology
from nats_bench.api_topology import ALL_BASE_NAMES as tss_base_names


class SearchSpace(Enum):
    TOPOLOGY = 1
    SIZE = 2


def extract_archs_benchmarks(benchmark_dir: str, search_space: SearchSpace) -> Dict[str, Dict]:
    if search_space == SearchSpace.TOPOLOGY:
      api = NATStopology(benchmark_dir, True, False)
    elif search_space == SearchSpace.SIZE:
      api = NATSsize(benchmark_dir, True, False)
    else:
      raise Exception("invalid search space")

    datasets = {
        'cifar10': 'CIFAR-10',
        'cifar100': 'CIFAR-100',
        'ImageNet16-120': 'ImageNet16-120'
    }
    if search_space == SearchSpace.TOPOLOGY:
        nums_epochs = {
            12: '12',
            200: '200'
        }
    else:
        nums_epochs = {
            1: '01',
            12: '12',
            90: '90'
        }
    archs = {}

    for arch_id in range(len(api)):
        print(f'Architecture {arch_id} topology: {api.arch(arch_id)}')
        arch_key = api.arch(arch_id)
        archs[arch_key] = {}

        # hack to free RAM
        if arch_id != 0 and arch_id % 1000 == 0:
            del api
            if search_space == SearchSpace.TOPOLOGY:
                api = NATStopology(benchmark_dir, True, False)
            elif search_space == SearchSpace.SIZE:
                api = NATSsize(benchmark_dir, True, False)

        for dataset_id, dataset_name in datasets.items():
            archs[arch_key][dataset_id] = {}
            for num_epochs, num_epochs_str in nums_epochs.items():
              arch_performance = api.get_more_info(arch_id, dataset_id, hp=num_epochs_str)
              archs[arch_key][dataset_id][num_epochs] = { #[
                # accuracy and time
                #arch_performance['train-loss'], arch_performance['train-accuracy'], arch_performance['train-all-time'], arch_performance['train-all-time'], arch_performance['test-accuracy'], arch_performance['test-all-time']

                "train_loss": arch_performance['train-loss'],
                "train_accuracy":  arch_performance['train-accuracy'],
                "train_time": arch_performance['train-all-time'],
                "test_loss": arch_performance['train-all-time'],
                "test_accuracy": arch_performance['test-accuracy'],
                "test_time": arch_performance['test-all-time'],
              } # ]

    return archs


benchmarks_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'benchmarks')
uncompressed_benchmark_dir_suffix = '-simple'

# architectures in topology search space
benchmark_dir = os.path.join(benchmarks_base_dir, tss_base_names[-1] + uncompressed_benchmark_dir_suffix)
archs = extract_archs_benchmarks(benchmark_dir, SearchSpace.TOPOLOGY)
with open('topology_ss_architectures.json', 'w') as fp:
   json.dump(archs, fp, indent=2, sort_keys=True)

# architectures in size search space
benchmark_dir = os.path.join(benchmarks_base_dir, sss_base_names[-1] + uncompressed_benchmark_dir_suffix)
archs = extract_archs_benchmarks(benchmark_dir, SearchSpace.SIZE)
with open('size_ss_architectures.json', 'w') as fp:
   json.dump(archs, fp, indent=2, sort_keys=True)
