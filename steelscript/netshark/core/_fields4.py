# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.




from steelscript.common.utils import DictObject

class ExtractorField(DictObject):
    @classmethod
    def get_all(cls, shark):
        return [cls(field) for field in shark.api.info.get_fields()]
