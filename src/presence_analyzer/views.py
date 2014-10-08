# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import render_template

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify, get_data, mean, group_by_weekday, presence_start_end)

import logging
log = logging.getLogger(__name__)  # pylint: disable=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return render_template('presence_weekday.html', page_url='mainpage')


@app.route('/mean_time_weekday')
def mean_time_weekday():
    """
    """
    return render_template(
        'mean_time_weekday.html', page_url='mean_time_weekday')


@app.route('/presence_start_end')
def presence_start_end_route():
    """
    """
    return render_template(
        'presence_start_end.html', page_url='presence_start_end_route')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
            for i in data.keys()]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in weekdays.items()
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns time intervals in which the selected user is usually present.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = presence_start_end(data[user_id])
    result = [
        (calendar.day_abbr[weekday], date_time['start'], date_time['end'])
        for weekday, date_time in weekdays.items()
    ]

    return result
