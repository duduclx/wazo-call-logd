# Copyright 2020-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from datetime import (
    datetime as dt,
    timedelta as td,
    timezone as tz,
)
from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    has_properties,
    none,
)

from wazo_call_logd.database.models import Recording

from .helpers.base import DBIntegrationTest
from .helpers.database import recording


class TestRecording(DBIntegrationTest):
    def test_create_all(self):
        end_time = dt.now(tz.utc)
        start_time = end_time - td(hours=1)
        recording_min = Recording(
            start_time=start_time,
            end_time=end_time,
            call_log_id=1234,
        )
        recording_full = Recording(
            start_time=start_time,
            end_time=end_time,
            path='/tmp/foo.wav',
            call_log_id=5678,
        )

        self.dao.recording.create_all([recording_min, recording_full])

        result = self.session.query(Recording).all()
        assert_that(
            result,
            contains_inanyorder(
                has_properties(
                    start_time=start_time,
                    end_time=end_time,
                    path=None,
                    call_log_id=1234,
                ),
                has_properties(
                    start_time=start_time,
                    end_time=end_time,
                    path='/tmp/foo.wav',
                    call_log_id=5678,
                ),
            ),
        )
        self.session.query(Recording).delete()
        self.session.commit()

    @recording(call_log_id=1)
    @recording(call_log_id=2)
    def test_delete_all(self, rec1, rec2):
        self.dao.recording.delete_all()

        result = self.session.query(Recording).all()
        assert_that(result, empty())

    @recording(call_log_id=1)
    @recording(call_log_id=2)
    @recording(call_log_id=3)
    def test_delete_all_by_call_log_ids(self, rec1, rec2, rec3):
        call_log_ids = [rec1['call_log_id'], rec3['call_log_id']]

        self.dao.recording.delete_all_by_call_log_ids(call_log_ids)

        result = self.session.query(Recording).all()
        assert_that(result, contains_inanyorder(has_properties(uuid=rec2['uuid'])))

    @recording(call_log_id=1)
    @recording(call_log_id=2)
    @recording(call_log_id=3)
    def test_find_all_by_call_log_ids(self, rec1, rec2, rec3):
        call_log_ids = [rec1['call_log_id'], rec3['call_log_id']]

        result = self.dao.recording.find_all_by_call_log_ids(call_log_ids)

        assert_that(
            result,
            contains_inanyorder(
                has_properties(uuid=rec1['uuid']),
                has_properties(uuid=rec3['uuid']),
            ),
        )

    @recording(call_log_id=1)
    @recording(call_log_id=2)
    def test_find_all_by_call_log_id(self, rec1, rec2):
        call_log_id = rec2['call_log_id']

        result = self.dao.recording.find_all_by_call_log_id(call_log_id)

        assert_that(
            result,
            contains_inanyorder(
                has_properties(uuid=rec2['uuid']),
            ),
        )

    @recording(call_log_id=1)
    @recording(call_log_id=2)
    def test_find_by(self, rec1, rec2):
        result = self.dao.recording.find_by(uuid=rec2['uuid'])
        assert_that(result, has_properties(uuid=rec2['uuid']))

        result = self.dao.recording.find_by(call_log_id=rec2['call_log_id'])
        assert_that(result, has_properties(uuid=rec2['uuid']))

        result = self.dao.recording.find_by(uuid=uuid.uuid4())
        assert_that(result, none())

        result = self.dao.recording.find_by(call_log_id=666)
        assert_that(result, none())

        result = self.dao.recording.find_by(
            uuid=rec1['uuid'], call_log_id=rec2['call_log_id']
        )
        assert_that(result, none())
