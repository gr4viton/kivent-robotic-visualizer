from kivy.app import App
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window


from kivent_core.gameworld import GameWorld
from kivent_core.managers.resource_managers import texture_manager


from kivy.uix.scrollview import ScrollView

# from kivent_maps import map_utils
# from kivent_maps.map_system import MapSystem


from kivent_core.rendering.svg_loader import SVGModelInfo
from kivent_core.systems.renderers import RotateRenderer
from kivent_core.systems.position_systems import PositionSystem2D
from kivent_core.systems.rotate_systems import RotateSystem2D
from kivent_cymunk.interaction import CymunkTouchSystem
from kivy.properties import StringProperty, NumericProperty
from functools import partial
from os.path import dirname, join, abspath


from test_game import TestGame


def get_asset_path(asset, asset_loc):
    return join(dirname(dirname(abspath(__file__))), asset_loc, asset)


# def _get_args_dict(fn, args, kwargs):
#    args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
#    return {**dict(zip(args_names, args)), **kwargs}

texture_manager.load_atlas(
    get_asset_path("background_objects.atlas", "assets")
)
# texture_manager.load_atlas(get_asset_path('dalek_objects.atlas','assets'))
# texture_manager.load_atlas(join(atlas_dir, 'robot_objects.atlas'))

print(join(dirname(dirname(abspath(__file__))), "assets", "glsl"))


class ScrollableLabel(ScrollView):
    text = StringProperty("")


class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_once(self.update_fps)

    def update_fps(self, dt):
        self.fps = str(int(Clock.get_fps()))
        Clock.schedule_once(self.update_fps, 0.05)


class DalekApp(App):
    ent_count = StringProperty("...")
    ultrasound_status = StringProperty("...")
    robot_states = StringProperty("...")

    info_text = StringProperty("...")
    damping = NumericProperty(0.2)
    # def __init__(self, **kwargs):
    #   super(App, self).__init__(**kwargs)
    #  return
    def build(self):
        # root.bind(size=self._update_rect, pos=self._update_rect)
        h = 700
        w = 1300
        # Config.set('kivy', 'show_fps', 1)
        # Config.set('kivy', 'desktop', 1)

        Config.set("graphics", "window_state", "maximized")
        Config.set("graphics", "position", "custom")
        Config.set("graphics", "height", h)
        Config.set("graphics", "width", w)
        Config.set("graphics", "top", 15)
        Config.set("graphics", "left", 4)
        # Config.set('graphics',
        # Config.set('graphics', 'multisamples', 0) # to correct bug from kivy 1.9.1 - https://github.com/kivy/kivy/issues/3576

        # Config.set('graphics', 'fullscreen', 'fake')
        # Config.set('graphics', 'fullscreen', 1)
        Window.clearcolor = (1, 1, 1, 1)
        self.root = TestGame()
        return self.root

    def on_stop(self):
        self.root.map.clear_maps()


if __name__ == "__main__":
    DalekApp().run()
