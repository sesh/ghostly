#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import time
import random

from subprocess import Popen, PIPE


@click.command()
@click.argument('ghostly_files', type=str, nargs=-1, required=True)
@click.option('--workers', default=2, type=int)
@click.option('--rand-wait', default=True, type=bool)
def run_fright(ghostly_files, workers, rand_wait):
    start = time.time()
    cmd = ['ghostly', *ghostly_files, '--browser', 'phantomjs']

    all_workers = []
    for w in range(workers):
        all_workers.append(Popen(cmd, stdout=PIPE, stdin=PIPE))
        if rand_wait:
            time.sleep(random.randint(1, 5))
    print('{} workers running...'.format(len(all_workers)))

    failures = []
    times = []
    for w in all_workers:
        w.wait()
        stdout, stderr = w.communicate()
        lines = stdout.decode().splitlines()
        times.append(float(lines[-1].split('in')[-1].strip().replace('s', '')))
        if '✔' not in lines[-2]:
            print('Test failure:')
            print('\n'.join(lines[-10:]))
            print('----')
            failures.append(lines)

    stop = time.time()
    taken = round(float(stop - start), 2)
    average = round(sum(times) / len(times), 2)
    maximum = round(max(times), 2)

    print('Passed: {}'.format(len(all_workers) - len(failures)))
    print('Failed: {}'.format(len(failures)))
    print('Completion times [avg: {}, max: {}, all: {}]'.format(average, maximum, times))
    print('Took {}s with {} workers'.format(taken, len(all_workers)))

if __name__ == '__main__':
    run_fright()
