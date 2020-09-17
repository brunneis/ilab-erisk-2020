#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
from threading import Thread, Lock
import yaml
import os

NUM_THREADS_PER_SUBREDDIT_POST_TYPE = 20


def loop(id, post_type, subreddit, start_timestamp, stop_timestamp, write_lock, output_file):
    ids = set()
    prev_ids_len = 0

    no_new_users_loop_limit = 100

    while start_timestamp < stop_timestamp:
        url = f'https://api.pushshift.io/reddit/search/{post_type}/?subreddit={subreddit}&sort=asc&sort_type=created_utc&size=1000'
        if start_timestamp:
            url += f'&after={start_timestamp}'

        done = False
        while not done:
            try:
                posts = requests.get(url,
                                     proxies={
                                         'http': 'http://localhost:9999',
                                         'https': 'http://localhost:9999'
                                     }).json()['data']
                done = True
            except Exception:
                # print(f'Could not retrieve {url}, retrying...')
                time.sleep(1)

        for post in posts:
            if post['author'] in ids:
                continue
            else:
                ids.add(post['author'])
                with write_lock:
                    output_file.write(f"{post['author']}\n")

        # No new users
        if prev_ids_len == len(ids):
            if no_new_users_loop_limit == 0:
                break
            no_new_users_loop_limit -= 1
        prev_ids_len = len(ids)

        try:
            start_timestamp = posts[-1]['created_utc'] - 1
        except IndexError:
            break
        finally:
            print(f'[THREAD_{subreddit.upper()}_{post_type.upper()}_{id}] {len(ids)}')


def extract_users(subreddit):
    start_timestamp = 1072915200  # 2004/01/01
    current_timestamp = int(round(time.time()))
    interval_length = int(
        (current_timestamp - start_timestamp) / NUM_THREADS_PER_SUBREDDIT_POST_TYPE)
    start_points = list(range(start_timestamp, current_timestamp + interval_length,
                              interval_length))
    print(start_points[:-1])

    base_dir = 'subreddits_users'
    try:
        os.mkdir(base_dir)
    except FileExistsError:
        pass

    output_file = open(f'{base_dir}/{subreddit}.csv', 'a')
    write_lock = Lock()

    threads = []
    for post_type in ['submission', 'comment']:
        for i, start_point in enumerate(start_points[:-1]):
            thread = Thread(target=loop,
                            args=[
                                i, post_type, subreddit, start_point, start_point + interval_length,
                                write_lock, output_file
                            ])
            threads.append(thread)
            thread.start()

    return threads, output_file


if __name__ == "__main__":
    subreddits = [
        'depression', 'depression_help', 'AnorexiaRecovery', 'AnorexiaNervosa', 'selfharm'
    ]
    threads = []
    output_files = []
    for subreddit in subreddits:
        subreddit_threads, subreddit_file = extract_users(subreddit)
        threads += subreddit_threads
        output_files.append(subreddit_file)

    for thread in threads:
        thread.join()
    for output_file in output_files:
        output_file.close()
