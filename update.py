#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Load latest packages into es
"""
import os
import json

import arrow
import bar
import pyes

from esutils import get_es, set_refresh, create_index

import config

LICENCE_CUSTOM_OR_UNKNOWN = 'custom_or_unknown'
LICENCES = ('bsd', 'mit', 'apache', 'lgpl', 'gpl', 'python',
            LICENCE_CUSTOM_OR_UNKNOWN)


def licence_sanitizer(licence):
    """
    Try to convert random junk from
    licence field into one of predefined licence types.
    """
    if licence in (None, 'UNKNOWN'):
        return LICENCE_CUSTOM_OR_UNKNOWN
    for licence_type in LICENCES[:-1]:
        if licence_type in licence.lower():
            return licence_type
    else:
        return LICENCE_CUSTOM_OR_UNKNOWN


def parse(data, run_id):
    result = {
        'description': data['info']['description'],
        'package_url': data['info']['package_url'],
        'summary': data['info']['summary'],
        'homepage': data['info']['home_page'],
        'version': data['info']['version'],
        'keywords': data['info']['keywords'],
        'name': data['info']['name'],
        'downloads.last_month': data['info']['downloads']['last_month'],
        'downloads.total': 0,
        'latest_release': None,
        'licence': None,
        'licence_clean': None,
        'run_id': run_id,
    }
    if data['info']['license'] is not None:
        #no, do not store WHOLE LICENCE CONTENT here.
        result['licence'] = data['info']['license'][:200]
    result['licence_sane'] = licence_sanitizer(result['licence'])
    total_downloads = 0
    release_dates = []
    for release_version, release_packagetypes in data['releases'].items():
        for package_type in release_packagetypes:
            release_dates.append(
                (release_version, arrow.get(package_type['upload_time']))
            )
            total_downloads += package_type['downloads']
    release_dates.sort(key=lambda x: x[1], reverse=True)
    if release_dates:
        result['latest_release'] = release_dates[0][1].datetime
    result['downloads.total'] = total_downloads

    return result


def push_to_es(data):
    #TODO: use bulk indexing
    get_es().index(data, config.ES_INDEX, config.ES_INDEX, id=data['name'])


def run():
    latest_id = os.path.split(os.path.realpath('packages/latest'))[-1]
    packages = next(os.walk('packages/latest'))[2]
    progressbar = bar.Bar(bar_max=len(packages))
    create_index()
    set_refresh(False)
    try:
        for pkg in packages:
            with open('packages/latest/' + pkg) as f:
                data = json.load(f)
                parsed_data = parse(data, run_id=latest_id)
                push_to_es(parsed_data)
            progressbar.step()
        es = get_es()
        es.delete_by_query(config.ES_INDEX, config.ES_DOC_TYPE, pyes.QueryStringQuery('-run_id:'+latest_id))
        es.indices.optimize(config.ES_INDEX)
        #fix weird pyes bug
        es.bulker = None
        print('Done')

    finally:
        set_refresh(True)

if __name__ == '__main__':
    run()
