from consts import *
from dataclasses import dataclass
from typing import Union, Optional
from range import Range
from rgb_container import RgbContainer
from functools import lru_cache


class DataclassDictCompatibility:
    def __getitem__(self, item: Union[str]):
        key = item.lower()
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"key ({item}) has to be one of: {list(self.__dataclass_fields__)}")

    def keys(self):
        return list(self.__dataclass_fields__)

    def values(self):
        return [getattr(self, key) for key in self.keys()]


@dataclass(frozen=True)
class OptimizerRecommendation(DataclassDictCompatibility):
    groove_width: float
    etching_depth: float
    refractive_index: float


@dataclass(frozen=True)
class OptimizerRecommendationMask(OptimizerRecommendation):
    groove_width: Union[float, bool]
    etching_depth: Union[float, bool]
    refractive_index: Union[complex, float, bool]

    def apply_to(self, guess: OptimizerRecommendation):
        return OptimizerRecommendation(
            groove_width=self.groove_width or guess.groove_width,
            etching_depth=self.etching_depth or guess.etching_depth,
            refractive_index=self.refractive_index or guess.refractive_index
        )


empty_mask = OptimizerRecommendationMask(False, False, False)


@dataclass(frozen=True)
class ColorMaterial(DataclassDictCompatibility):
    tio2: OptimizerRecommendation
    si3n4: OptimizerRecommendation
    fs: OptimizerRecommendation
    polymer1: OptimizerRecommendation
    polymer2: OptimizerRecommendation
    polymer3: OptimizerRecommendation


@dataclass(frozen=True, init=False)
class _RefractiveIndices(DataclassDictCompatibility):
    tio2: RgbContainer = RgbContainer(
        # red=2.311891,
        # green=2.378428,
        # blue=2.461716
        red=2.311891 + 0.000000j,
        green=2.378428 + 0.000004j,
        blue=2.461716 + 0.000085j
    )
    si3n4: RgbContainer = RgbContainer(
        red=2.0389,
        green=2.0585,
        blue=2.0786
    )
    sio2: RgbContainer = RgbContainer(
        red=1.4569,
        green=1.4613,
        blue=1.4656
    )

    polymer1: RgbContainer = RgbContainer(
        # TODO: verify polymer numbers! ( they are marked with question marks in the document)
        red=1.7,
        green=1.7,
        blue=1.7
    )
    polymer2: RgbContainer = RgbContainer(
        red=1.8,
        green=1.8,
        blue=1.8
    )
    polymer3: RgbContainer = RgbContainer(
        red=1.89,
        green=1.89,
        blue=1.89
    )

    def material_from_index(self, refractive_index):
        for material, container in dict(self).items():
            if refractive_index in container:
                return material
        raise KeyError(f'No material with refractive index of {refractive_index} found')


RefractiveIndices = _RefractiveIndices()


# color_materials = RgbContainer(
#     red=ColorMaterial(**{
#         'tio2': OptimizerRecommendation(
#             groove_width=0.000281758, etching_depth=0.0017705, refractive_index=RefractiveIndices.tio2.red),
#         'si3n4': OptimizerRecommendation(
#             groove_width=0.00015, etching_depth=0.00115055, refractive_index=RefractiveIndices.si3n4.red),
#         'fs': OptimizerRecommendation(
#             groove_width=0.00034129, etching_depth=0.002, refractive_index=RefractiveIndices.fs.red),
#         'polymer1': OptimizerRecommendation(
#             groove_width=0.00015374, etching_depth=0.00140295, refractive_index=RefractiveIndices.polymer1.red),
#         'polymer2': OptimizerRecommendation(
#             groove_width=0.00015374, etching_depth=0.00140295, refractive_index=RefractiveIndices.polymer2.red),
#         'polymer3': OptimizerRecommendation(
#             groove_width=0.00015374, etching_depth=0.00140295, refractive_index=RefractiveIndices.polymer3.red),
#     }),
#     green=ColorMaterial(**{
#         'tio2': OptimizerRecommendation(
#             groove_width=0.0002721, etching_depth=0.001525, refractive_index=RefractiveIndices.tio2.green),
#         'si3n4': OptimizerRecommendation(
#             groove_width=0.00015, etching_depth=0.00062898, refractive_index=RefractiveIndices.si3n4.green),
#         'fs': OptimizerRecommendation(
#             groove_width=0.00019779, etching_depth=0.00147225, refractive_index=RefractiveIndices.fs.green),
#         'polymer1': OptimizerRecommendation(
#             groove_width=0.00015998, etching_depth=0.00073161, refractive_index=RefractiveIndices.polymer1.green),
#         'polymer2': OptimizerRecommendation(
#             groove_width=0.00015998, etching_depth=0.00073161, refractive_index=RefractiveIndices.polymer2.green),
#         'polymer3': OptimizerRecommendation(
#             groove_width=0.00015998, etching_depth=0.00073161, refractive_index=RefractiveIndices.polymer3.green),
#     }),
#     blue=ColorMaterial(**{
#         'tio2': OptimizerRecommendation(
#             groove_width=0.000196149, etching_depth=0.0027944, refractive_index=RefractiveIndices.tio2.blue),
#         'si3n4': OptimizerRecommendation(
#             groove_width=0.00015107, etching_depth=0.00100099, refractive_index=RefractiveIndices.si3n4.blue),
#         'fs': OptimizerRecommendation(
#             groove_width=0.00016461, etching_depth=0.00073301, refractive_index=RefractiveIndices.fs.blue),
#         'polymer1': OptimizerRecommendation(
#             groove_width=0.00018645, etching_depth=0.00146155, refractive_index=RefractiveIndices.polymer1.blue),
#         'polymer2': OptimizerRecommendation(
#             groove_width=0.00018645, etching_depth=0.00146155, refractive_index=RefractiveIndices.polymer2.blue),
#         'polymer3': OptimizerRecommendation(
#             groove_width=0.00018645, etching_depth=0.00146155, refractive_index=RefractiveIndices.polymer3.blue),
#     }))


# @dataclass(frozen=True)
# class MaterialSidewallAngle(DataclassDictCompatibility):
#     tio2 = 0.0
#     si3n4 = 5.0
#     sio2 = 5.0
#     polymer1 = 0.0
#     polymer2 = 0.0
#     polymer3 = 0.0
#
#
# MaterialSidewallAngle = MaterialSidewallAngle()


@dataclass(frozen=True)
class Cost:
    main_color_efficiency: Union[float, np.ndarray]
    main_color_std: Union[float, np.ndarray]
    main_color_transparency_efficiency: Union[float, np.ndarray]
    main_color_transparency_std: Union[float, np.ndarray]
    other_color_efficiency_1: Union[float, np.ndarray]
    other_color_std_1: Union[float, np.ndarray]
    other_color_transparency_efficiency_1: Union[float, np.ndarray]
    other_color_transparency_std_1: Union[float, np.ndarray]
    other_color_efficiency_2: Union[float, np.ndarray]
    other_color_std_2: Union[float, np.ndarray]
    other_color_transparency_efficiency_2: Union[float, np.ndarray]
    other_color_transparency_std_2: Union[float, np.ndarray]
    total_cost: Union[float, np.ndarray]


@dataclass(frozen=True)
class OptimizationResult:
    recommendation: OptimizerRecommendation
    cost: Cost


@dataclass()
class CostParameters:
    color: Color
    main: np.ndarray  # diffraction for the main color, transmission for everything else
    main_std: np.ndarray
    secondary: Optional[np.ndarray]  # transparency transmission
    secondary_std: Optional[np.ndarray]


@dataclass(frozen=True)
class SingleMaterial:
    name: str
    refractive_index: RgbContainer
    line_width_minimum: float
    groove_minimum: float
    etching_depth_maximum: float
    line_max_aspect_ratio: float
    groove_max_aspect_ratio: float
    sidewall_angle: int
    scale_factor: Optional[float] = 4

    def get_normalizer(self, period: float):
        etching_depth = (200 * nm, self.etching_depth_maximum)
        line_width = (self.line_width_minimum,
                      period - self.groove_minimum)
        groove_width = (self.groove_minimum,
                        period - self.line_width_minimum)
        if line_width[0] > line_width[1] or groove_width[0] > groove_width[1] or etching_depth[0] > etching_depth[1]:
            logger.warning(f"bounds issue for {self.name}: line width: {line_width}, groove_width: {groove_width}, "
                        f"etching depth: {etching_depth}")
            pass
        return Normalizer(
            line_width=Range(line_width),
            groove_width=Range(groove_width),
            etching_depth=Range(etching_depth),
            scale_factor=self.scale_factor
        )


@dataclass(frozen=True)
class Normalizer(DataclassDictCompatibility):
    line_width: Range
    groove_width: Range
    etching_depth: Range
    scale_factor: Optional[float] = 1

    def normalize(self, recommendation=Union[OptimizerRecommendation, OptimizerRecommendationMask],
                  round: bool = False):
        groove_width = self.groove_width.normalize_param(recommendation.groove_width)
        if type(groove_width) is not bool:
            groove_width *= self.scale_factor
            # if our initial guess is out of bounds, round it to the nearest bound
            if round:
                if groove_width > self.scale_factor:
                    logger.debug(
                        f'initial suggestion groove width is too large ({recommendation.groove_width} -> {groove_width}), '
                        f'rounding to: {self.scale_factor}')
                    groove_width = self.scale_factor
                elif groove_width < -self.scale_factor:
                    logger.debug(
                        f'initial suggestion groove width is too small ({recommendation.groove_width} -> {groove_width}), '
                        f'rounding to: {-self.scale_factor}')
                    groove_width = -self.scale_factor

        etching_depth = self.etching_depth.normalize_param(recommendation.etching_depth)
        if type(etching_depth) is not bool:
            etching_depth *= self.scale_factor
            # if our initial guess is out of bounds, round it to the nearest bound
            if round:
                if etching_depth > self.scale_factor:
                    logger.debug(
                        f'initial etching depth is too large ({recommendation.etching_depth} -> {etching_depth}), '
                        f'rounding to: {self.scale_factor}')
                    etching_depth = self.scale_factor
                elif etching_depth < -self.scale_factor:
                    logger.debug(
                        f'initial etching depth is too small ({recommendation.etching_depth} -> {etching_depth}), '
                        f'rounding to: {-self.scale_factor}')
                    etching_depth = -self.scale_factor

        # result of the same type as the input
        return type(recommendation)(
            groove_width=groove_width,
            etching_depth=etching_depth,
            refractive_index=recommendation.refractive_index
        )

    def denormalize(self, recommendation=Union[OptimizerRecommendation, OptimizerRecommendationMask]):
        if type(recommendation.groove_width) is bool:
            groove_width = self.groove_width.denormalize_param(recommendation.groove_width)
        else:
            groove_width = self.groove_width.denormalize_param(
                recommendation.groove_width / self.scale_factor)

        if type(recommendation.etching_depth) is bool:
            etching_depth = self.etching_depth.denormalize_param(recommendation.etching_depth)
        else:
            etching_depth = self.etching_depth.denormalize_param(
                recommendation.etching_depth / self.scale_factor)

        # result of the same type as the input
        return type(recommendation)(
            groove_width=groove_width,
            etching_depth=etching_depth,
            refractive_index=recommendation.refractive_index
        )


@dataclass(frozen=True)
class _Material(DataclassDictCompatibility):
    tio2: SingleMaterial
    sio2: SingleMaterial
    si3n4: SingleMaterial
    polymer1: SingleMaterial
    polymer2: SingleMaterial
    polymer3: SingleMaterial

    def __getitem__(self, item) -> SingleMaterial:
        return super(_Material, self).__getitem__(item)


Material = _Material(
    tio2=SingleMaterial(name='tio2', refractive_index=RefractiveIndices.tio2,
                        line_width_minimum=100 * nm,
                        groove_minimum=100 * nm,
                        etching_depth_maximum=2500 * nm,
                        line_max_aspect_ratio=10.,
                        groove_max_aspect_ratio=10.,
                        sidewall_angle=0),
    sio2=SingleMaterial(name='sio2', refractive_index=RefractiveIndices.sio2,
                        line_width_minimum=100 * nm,
                        groove_minimum=100 * nm,
                        etching_depth_maximum=2500 * nm,
                        line_max_aspect_ratio=10.,
                        groove_max_aspect_ratio=4.,
                        sidewall_angle=0),
    si3n4=SingleMaterial(name='si3n4', refractive_index=RefractiveIndices.si3n4,
                         line_width_minimum=100 * nm,
                         groove_minimum=100 * nm,
                         etching_depth_maximum=1500 * nm,
                         line_max_aspect_ratio=4.,
                         groove_max_aspect_ratio=4.,
                         sidewall_angle=5),
    polymer1=SingleMaterial(name='polymer1', refractive_index=RefractiveIndices.polymer1,
                            line_width_minimum=170 * nm,
                            groove_minimum=170 * nm,
                            etching_depth_maximum=600 * nm,
                            line_max_aspect_ratio=3.571428,
                            groove_max_aspect_ratio=5.,
                            sidewall_angle=0),
    polymer2=SingleMaterial(name='polymer2', refractive_index=RefractiveIndices.polymer2,
                            line_width_minimum=170 * nm,
                            groove_minimum=170 * nm,
                            etching_depth_maximum=600 * nm,
                            line_max_aspect_ratio=3.571428,
                            groove_max_aspect_ratio=5.,
                            sidewall_angle=0),
    polymer3=SingleMaterial(name='polymer3', refractive_index=RefractiveIndices.polymer3,
                            line_width_minimum=170 * nm,
                            groove_minimum=170 * nm,
                            etching_depth_maximum=600 * nm,
                            line_max_aspect_ratio=3.571428,
                            groove_max_aspect_ratio=5.,
                            sidewall_angle=0),
)
