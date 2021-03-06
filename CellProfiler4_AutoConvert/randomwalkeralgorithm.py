# coding=utf-8

"""

Random walker algorithm

Single-channel images can be two-or-three-dimensional.

"""

import numpy
import skimage.color
import skimage.measure
import skimage.segmentation

import cellprofiler_core.module
import cellprofiler_core.object
import cellprofiler_core.setting
from cellprofiler_core.module.image_segmentation import ImageSegmentation
from cellprofiler_core.setting.text import Float


class RandomWalkerAlgorithm(ImageSegmentation):
    module_name = "Random walker algorithm"

    variable_revision_number = 1

    def create_settings(self):
        super(RandomWalkerAlgorithm, self).create_settings()

        self.first_phase = Float(
            doc="First phase demarcates an image’s first phase.",
            text="First phase",
            value=0.5
        )

        self.second_phase = Float(
            doc="Second phase demarcates an image’s second phase.",
            text="Second phase",
            value=0.5
        )

        self.beta = Float(
            doc="""
                Beta is the penalization coefficient for the random walker motion. Increasing the penalization
                coefficient increases the difficulty of the diffusion. Likewise, decreasing the penalization coefficient
                decreases the difficulty of the diffusion.
            """,
            text="Beta",
            value=130.0
        )

    def settings(self):
        __settings__ = super(RandomWalkerAlgorithm, self).settings()

        return __settings__ + [
            self.first_phase,
            self.second_phase,
            self.beta
        ]

    def visible_settings(self):
        __settings__ = super(RandomWalkerAlgorithm, self).settings()

        return __settings__ + [
            self.first_phase,
            self.second_phase,
            self.beta
        ]

    def run(self, workspace):
        x_name = self.x_name.value

        y_name = self.y_name.value

        images = workspace.image_set

        x = images.get_image(x_name)

        x_data = x.pixel_data

        if x.multichannel:
            x_data = skimage.color.rgb2gray(x_data)

        labels_data = numpy.zeros_like(x_data, numpy.uint8)

        labels_data[x_data > self.first_phase.value] = 1

        labels_data[x_data < self.second_phase.value] = 2

        y_data = skimage.segmentation.random_walker(
            beta=self.beta.value,
            data=x_data,
            labels=labels_data,
            multichannel=False,
            spacing=x.spacing
        )

        y_data = skimage.measure.label(y_data)

        objects = cellprofiler_core.object.Objects()

        objects.segmented = y_data

        objects.parent_image = x

        workspace.object_set.add_objects(objects, y_name)

        self.add_measurements(workspace)

        if self.show_window:
            workspace.display_data.x_data = x_data

            workspace.display_data.y_data = y_data

            workspace.display_data.dimensions = x.dimensions
