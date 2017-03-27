# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo.auth_verifier import required_acl
from xivo_call_logs.core.rest_api import AuthResource

from .schema import cdr_schema


class CDRResource(AuthResource):

    def __init__(self, cdr_service):
        self.cdr_service = cdr_service

    @required_acl('call_logd.cdr.read')
    def get(self):
        cdrs = self.cdr_service.list()

        return {'items': cdr_schema.dump(cdrs, many=True).data}
