"""
ARM route blueprint for notifications pages
Covers
- arm_nav_notify [GET]
- arm_notification [GET]
- arm_notification_close [GET}
"""

from flask_login import login_required  # noqa: F401
from flask import render_template, Blueprint, redirect
from datetime import datetime

import arm.ui.utils as ui_utils
from arm.ui import app
from arm.models import models as models

route_notifications = Blueprint('route_notifications', __name__,
                                template_folder='templates',
                                static_folder='../static')


@app.context_processor
@login_required
def arm_nav_notify():
    """
    inject the unread notification count to all pages for the navbar count
    """
    notify_count = models.Notifications.query.filter_by(seen='0').count()
    app.logger.debug(notify_count)
    return dict(notify_count=notify_count)


@route_notifications.route('/notificationview')
@login_required
def arm_notification():
    """
    function to display all current notifications
    """
    notifications_new = models.Notifications.query.filter_by(seen='0').order_by(models.Notifications.id.desc()).all()

    if len(notifications_new) != 0:
        # get the current time for each notification and then save back into notification
        for notification in notifications_new:
            notification.diff_time = datetime.now().replace(microsecond=0) - notification.trigger_time
    else:
        notifications_new = None

    return render_template('notificationview.html',
                           notifications_new=notifications_new)


@route_notifications.route('/notificationclose')
@login_required
def arm_notification_close():
    """
    function to close all open notifications
    """
    notifications = models.Notifications.query.filter_by(seen='0').all()

    if len(notifications) != 0:
        # get the current time for each notification and then save back into notification
        for notification in notifications:
            args = {
                'seen': True,
                'dismiss_time': datetime.now()
            }
            ui_utils.database_updater(args, notification)

    return redirect("/notificationview")
