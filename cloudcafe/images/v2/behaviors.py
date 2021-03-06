"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import calendar
import time

from cafe.engine.behaviors import BaseBehavior
from cloudcafe.common.exceptions import BuildErrorException, TimeoutException
from cloudcafe.common.resources import ResourcePool
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.constants import ImageProperties, Messages
from cloudcafe.images.common.types import ImageContainerFormat, \
    ImageDiskFormat, ImageStatus, Schemas


class ImagesBehaviors(BaseBehavior):
    """@summary: Behaviors class for images v2"""

    def __init__(self, images_client, images_config):
        super(ImagesBehaviors, self).__init__()
        self.config = images_config
        self.client = images_client
        self.resources = ResourcePool()
        self.error_msg = Messages.ERROR_MSG
        self.id_regex = re.compile(ImageProperties.ID_REGEX)

    def create_new_image(self, container_format=None, disk_format=None,
                         name=None, protected=None, tags=None,
                         visibility=None):
        """@summary: Create new image and add it for deletion"""

        if container_format is None:
            container_format = ImageContainerFormat.BARE
        if disk_format is None:
            disk_format = ImageDiskFormat.RAW
        if name is None:
            name = rand_name('image')

        response = self.client.create_image(
            container_format=container_format, disk_format=disk_format,
            name=name, protected=protected, tags=tags, visibility=visibility)
        image = response.entity
        if image is not None:
            self.resources.add(image.id_, self.client.delete_image)
        return image

    def create_new_images(self, container_format=None, disk_format=None,
                          name=None, protected=None, tags=None,
                          visibility=None, count=1):
        """@summary: Create new images and add them for deletion"""

        image_list = []
        for i in range(count):
            image = self.create_new_image(
                container_format=container_format, disk_format=disk_format,
                name=name, protected=protected, tags=tags,
                visibility=visibility)
            image_list.append(image)
        return image_list

    def list_images_pagination(self, changes_since=None, checksum=None,
                               container_format=None, disk_format=None,
                               limit=None, marker=None, member_status=None,
                               min_disk=None, min_ram=None, name=None,
                               owner=None, protected=None, size_max=None,
                               size_min=None, sort_dir=None, sort_key=None,
                               status=None, visibility=None):
        """@summary: Get images accounting for pagination as needed"""

        image_list = []
        results_limit = self.config.results_limit
        response = self.client.list_images(
            changes_since=changes_since, checksum=checksum,
            container_format=container_format, disk_format=disk_format,
            limit=limit, marker=marker, member_status=member_status,
            min_disk=min_disk, min_ram=min_ram, name=name, owner=owner,
            protected=protected, size_max=size_max, size_min=size_min,
            sort_dir=sort_dir, sort_key=sort_key, status=status,
            visibility=visibility)
        images = response.entity
        while len(images) == results_limit:
            image_list += images
            marker = images[results_limit - 1].id_
            response = self.client.list_images(
                changes_since=changes_since, checksum=checksum,
                container_format=container_format, disk_format=disk_format,
                limit=limit, marker=marker, member_status=member_status,
                min_disk=min_disk, min_ram=min_ram, name=name, owner=owner,
                protected=protected, size_max=size_max, size_min=size_min,
                sort_dir=sort_dir, sort_key=sort_key, status=status,
                visibility=visibility)
            images = response.entity
        image_list += images
        return image_list

    def get_member_ids(self, image_id):
        """
        @summary: Return a complete list of ids for all members for a given
        image id
        """

        response = self.client.list_members(image_id)
        members = response.entity
        return [member.member_id for member in members]

    @staticmethod
    def get_creation_offset(image_creation_time_in_sec, time_property):
        """
        @summary: Calculate and return the difference between the image
        creation time and a given image time_property
        """

        time_property_in_sec = calendar.timegm(time_property.timetuple())
        return abs(time_property_in_sec - image_creation_time_in_sec)

    def validate_image(self, image):
        """@summary: Generically validate an image contains crucial expected
        data
        """

        errors = []
        if image.created_at is None:
            errors.append(self.error_msg.format('created_at', not None, None))
        if image.file_ != '/v2/images/{0}/file'.format(image.id_):
            errors.append(self.error_msg.format(
                'file_', '/v2/images/{0}/file'.format(image.id_), image.file_))
        if self.id_regex.match(image.id_) is None:
            errors.append(self.error_msg.format('id_', not None, None))
        if image.min_disk is None:
            errors.append(self.error_msg.format('min_disk', not None, None))
        if image.min_ram is None:
            errors.append(self.error_msg.format('min_ram', not None, None))
        if image.protected is None:
            errors.append(self.error_msg.format('protected', not None, None))
        if image.schema != Schemas.IMAGE_SCHEMA:
            errors.append(self.error_msg.format(
                'schema', Schemas.IMAGE_SCHEMA, image.schema))
        if image.self_ != '/v2/images/{0}'.format(image.id_):
            errors.append(self.error_msg.format(
                'schema', '/v2/images/{0}'.format(image.id_), image.self_))
        if image.status is None:
            errors.append(self.error_msg.format('status', not None, None))
        if image.updated_at is None:
            errors.append(self.error_msg.format('updated_at', not None, None))
        return errors

    def validate_image_member(self, image_id, image_member, member_id):
        """@summary: Generically validate an image member contains crucial
        expected data
        """

        errors = []
        if image_member.created_at is None:
            errors.append(self.error_msg.format('created_at', not None, None))
        if image_member.image_id != image_id:
            errors.append(self.error_msg.format(
                'image_id', image_id, image_member.image_id))
        if image_member.member_id != member_id:
            errors.append(self.error_msg.format(
                'member_id', member_id, image_member.member_id))
        if image_member.schema != Schemas.IMAGE_MEMBER_SCHEMA:
            errors.append(self.error_msg.format(
                'schema', Schemas.IMAGE_MEMBER_SCHEMA, image_member.schema))
        if image_member.status is None:
            errors.append(self.error_msg.format('status', not None, None))
        if image_member.updated_at is None:
            errors.append(self.error_msg.format('updated_at', not None, None))
        return errors

    def wait_for_image_status(self, image_id, desired_status,
                              interval_time=None, timeout=None):
        """
        @summary: Waits for a image to reach a desired status
        @param image_id: The uuid of the image
        @type image_id: String
        @param desired_status: The desired final status of the image
        @type desired_status: String
        @param interval_time: The amount of time in seconds to wait
                              between polling
        @type interval_time: Integer
        @param timeout: The amount of time in seconds to wait
                              before aborting
        @type timeout: Integer
        @return: Response object containing response and the image
                 domain object
        @rtype: requests.Response
        """

        interval_time = interval_time or self.config.image_status_interval
        timeout = timeout or self.config.snapshot_timeout
        end_time = time.time() + timeout

        while time.time() < end_time:
            resp = self.client.get_image(image_id)
            image = resp.entity

            if image.status.lower() == ImageStatus.ERROR.lower():
                raise BuildErrorException(
                    "Build failed. Image with uuid {0} "
                    "entered ERROR status.".format(image.id))

            if image.status == desired_status:
                break
            time.sleep(interval_time)
        else:
            raise TimeoutException(
                "wait_for_image_status ran for {0} seconds and did not "
                "observe image {1} reach the {2} status.".format(
                    timeout, image_id, desired_status))

        return resp
