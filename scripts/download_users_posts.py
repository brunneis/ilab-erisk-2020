#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys
import os


def clean_text(text):
    empty = not text or not isinstance(text, str) or text in [
        'removed by moderator', '[deleted]', '[removed]'
    ]
    if empty:
        return ''
    return ' '.join(text.replace('\n', '').replace('\r', '').split()).strip()


def extract_post(post_type, post):
    content = {'title': '', 'body': ''}
    try:
        if post_type == 'submission':
            if post['title']:
                content['title'] = clean_text(post['title'])
            if 'selftext' in post and post['selftext']:
                content['body'] = clean_text(post['selftext'])
        elif post_type == 'comment':
            content['body'] = clean_text(post['body'])
    except Exception:
        print(f'[ERROR] {post}')
    return content


def extract_posts(base_dir, user, post_type):
    with open(f'{base_dir}/{user}_{post_type}.csv', 'a') as output_file:
        start_timestamp = 0
        ids = set()
        prev_ids_len = -1
        while prev_ids_len != len(ids):
            prev_ids_len = len(ids)

            if prev_ids_len >= 15000:
                output_file.write('\nDELETE\n')
                return

            url = f'https://api.pushshift.io/reddit/search/{post_type}/?author={user}&after={start_timestamp}&sort=asc&sort_type=created_utc&size=1000'

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
                    # print(f'\033[91m[WARN]\033[0m {url}')
                    time.sleep(5)
                    pass

            print(f'\033[92m[OK]\033[0m {url}')

            for post in posts:
                try:
                    ids.add(post['id'])
                    extracted_post = extract_post(post_type, post)
                    extracted_post['timestamp'] = post['created_utc']
                    extracted_post['subreddit'] = post['subreddit']
                    extracted_post['score'] = post['score']
                    extracted_post[f'{post_type}_id'] = post['id']
                    extracted_post['text_type'] = post_type
                    if post_type == 'submission':
                        extracted_post['is_self'] = post['is_self']
                    else:
                        extracted_post['is_self'] = True
                    output_file.write(
                        f"{json.dumps(extracted_post, separators=(',', ':'), ensure_ascii=False)}\n"
                    )
                except Exception as e:
                    print(e)
                    continue

            try:
                start_timestamp = posts[-1]['created_utc'] - 1
            except IndexError:
                break
            finally:
                print(f'\033[94m[{user}/{post_type}]\033[0m {len(ids)}')


from threading import Thread
from multiprocessing import Process


def launch_user_threads(base_dir, user):
    t1 = Thread(target=extract_posts, args=[base_dir, user, 'submission'])
    t2 = Thread(target=extract_posts, args=[base_dir, user, 'comment'])

    t1.start()
    t2.start()

    t1.join()
    t2.join()


def launch_process(base_dir, user):
    p1 = Process(target=launch_user_threads, args=[base_dir, user])
    p1.start()
    return p1


if __name__ == "__main__":
    # ./download_users_posts.py users_file

    if len(sys.argv) < 2:
        raise SystemExit

    users_file = sys.argv[1]
    subreddit = ''.join(''.join(users_file.split('/')[-1]).split('_users.txt')[:-1])
    base_dir = f'posts-by-user/{subreddit}'

    try:
        os.mkdir(base_dir)
    except FileExistsError:
        pass

    with open(users_file, 'r') as input_file:
        running_processes = []

        user_counter = 0
        for user in input_file:
            print(f'\033[93m[USERS]\033[0m {user_counter}')
            user = user.strip()

            p1 = launch_process(base_dir, user)
            running_processes.append(p1)
            user_counter += 1

            done = False
            while not done:
                new_running_processes = []
                for process in running_processes:
                    if process.is_alive():
                        new_running_processes.append(process)
                running_processes = new_running_processes

                if len(running_processes) < 10000:
                    done = True
                else:
                    time.sleep(1)

        for process in running_processes:
            process.join()
