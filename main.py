from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.config import Config

import pickle

import magic
import globals as glob


def save_data(self):
    '''Saves the data into a pickle file for reuse later.'''
    pickle_data = self
    filename = "saved_data.pickle"
    pickle_out = open(filename, "wb")
    pickle.dump(pickle_data, pickle_out)
    pickle_out.close()


def load_data(self):
    '''Loads the data from a pickle file and reads to the list'''
    filename = "saved_data.pickle"
    pickle_in = open(filename, 'rb')
    reloaded_list = pickle.load(pickle_in)
    for i in range(len(reloaded_list)):
        self[i] = reloaded_list[i]


def load_default_data(self):
    filename = "default_data.pickle"
    pickle_in = open(filename, 'rb')
    reloaded_list = pickle.load(pickle_in)
    for i in range(len(reloaded_list)):
        self[i] = reloaded_list[i]


class Fitnessapp(Screen):
    Builder.load_file("ui.kv")
    needed_list = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        data_saved = [{}, [], {}, []]
        try:
            load_data(data_saved)
            glob.user_profile = data_saved[0]
            glob.allfooditems = data_saved[1]
            # glob.current_food_sum = data_saved[2]
            glob.food_choices = data_saved[3]
        except EOFError:
            print('Loading defaults')
        self.show_recomend()

    def on_pre_enter(self):
        Window.size = (720, 1280)

    def sumbit_food_click(self):
        newDict = {"name": self.ids.name_input.text, "calories": self.ids.calories_input.text,
                   "proteins": self.ids.proteins_input.text, "fats": self.ids.fats_input.text,
                   "carbs": self.ids.carbs_input.text, "pressed_amount": 0}
        if newDict not in glob.allfooditems:
            glob.allfooditems.append(newDict)



    def show_recomend(self):
        print(glob.allfooditems)
        glob.needed_macros = calculate_def_macros(glob.user_profile)
        self.ids.calories_show.text = "kkal\n" + str(glob.current_food_sum["calories"]) + "/" + str(
            glob.needed_macros[0])
        self.ids.proteins_show.text = "proteins\n" + str(glob.current_food_sum["proteins"]) + "/" + str(
            glob.needed_macros[1])
        self.ids.fats_show.text = "fats\n" + str(glob.current_food_sum["fats"]) + "/" + str(glob.needed_macros[2])
        self.ids.carbs_show.text = "carbs\n" + str(glob.current_food_sum["carbs"]) + "/" + str(glob.needed_macros[3])


        # MainApp.stop(MainApp())



class BoxButton(ToggleButtonBehavior, MDBoxLayout):
    def __init__(self, **kwargs):
        super(BoxButton, self).__init__(**kwargs)

    def change_current_food_sum(self, sign):
        glob.current_food_sum["calories"] += round(
            float(glob.allfooditems[int(self.id)]["calories"]) * glob.allfooditems[int(self.id)]["pressed_amount"] * sign)
        glob.current_food_sum["proteins"] += round(
            float(glob.allfooditems[int(self.id)]["proteins"]) * glob.allfooditems[int(self.id)]["pressed_amount"] * sign)
        glob.current_food_sum["fats"] += round(float(glob.allfooditems[int(self.id)]["fats"]) * glob.allfooditems[int(self.id)]["pressed_amount"] * sign)
        glob.current_food_sum["carbs"] += round(float(glob.allfooditems[int(self.id)]["carbs"]) * glob.allfooditems[int(self.id)]["pressed_amount"] * sign)
        self.parent.parent.parent.selected_foods.text = "kkal: " + str(glob.current_food_sum["calories"]) + \
                                                        "\nproteins: " + str(glob.current_food_sum["proteins"]) + \
                                                        "  fats: " + str(
            glob.current_food_sum["fats"]) + "  carbs: " + str(
            glob.current_food_sum["carbs"])

    def on_state(self, widget, value):
        if value == 'down':
            if glob.allfooditems[int(self.id)]["pressed_amount"] == 0:
                AmountAskPopup(widget=self).open()
            else:
                self.change_current_food_sum(1)
            self._md_bg_color = [0.7, 0.5, 0.5, 0.8]

        else:
            self._md_bg_color = [1, 1, 1, .5]
            self.change_current_food_sum(-1)
            glob.allfooditems[int(self.id)]["pressed_amount"] = 0

class HelpButton (ToggleButton):
    def on_state(self, widget, value):
        # if self.state == 'down' else app.theme_cls.primary_light
        if value == 'down':
            self.parent.parent.food_help()
            self.call_apriori()
        else:
            self.text = 'Help'
            for each in self.parent.parent.needed_list.children[2:]:
                if glob.allfooditems[int(each.id)]['pressed_amount'] == 0:
                    each._md_bg_color = [1, 1, 1, 0.5]
                else:
                    each._md_bg_color = [0.7, 0.5, 0.5, 0.8]

        MainApp.help_counter += 1
    def call_apriori(self):
        print(glob.food_choices)
        result = magic.apriori(glob.food_choices,0.01,0.01,0.01,10)
        for each in result:
            print(''.join(each[0])+','+each[2]+','+str(each[3])+','+str(each[4]))
        current_pressed = set()
        for each in glob.allfooditems:
            if each['pressed_amount'] > 0:
                current_pressed.add(each['name'])
        for rules_data in result:
            condition = set(rules_data[2].split(' '))
            full_set = set(rules_data[0].split(' '))
            if current_pressed == condition:
                if rules_data[4]>1 and len(full_set)-len(condition)==1:
                    diff = full_set.difference(condition)
                    self.text=str(diff.pop())





class AmountAskPopup(Popup):
    widget = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_popup_to_calcs(self, text):
        glob.allfooditems[int(self.widget.id)]["pressed_amount"] = float(text)
        self.widget.change_current_food_sum(1)


class FoodNavigationItem(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def food_help(self):
        for each in self.needed_list.children[2:]:
            if float(glob.allfooditems[int(each.id)]["calories"]) * 3 < glob.needed_macros[0] and \
                    float(glob.allfooditems[int(each.id)]["proteins"]) * 3 < glob.needed_macros[1] and \
                    float(glob.allfooditems[int(each.id)]["fats"]) * 3 < glob.needed_macros[2] and \
                    float(glob.allfooditems[int(each.id)]["carbs"]) * 3 < glob.needed_macros[3] and \
                    float(glob.allfooditems[int(each.id)]["carbs"])*4/float(glob.allfooditems[int(each.id)]["calories"])<0.9:
                if glob.allfooditems[int(each.id)]["pressed_amount"]>0:
                    each._md_bg_color = [0, 0.7, 0, 0.7]
                else:
                    each._md_bg_color = [0, 1, 0, 0.5]
            elif float(glob.allfooditems[int(each.id)]["calories"]) * 1 < glob.needed_macros[0] - float(
                    glob.current_food_sum["calories"]) and \
                    float(glob.allfooditems[int(each.id)]["proteins"]) * 1 < glob.needed_macros[1] - float(
                glob.current_food_sum["proteins"]) and \
                    float(glob.allfooditems[int(each.id)]["fats"]) * 1 < glob.needed_macros[2] - float(
                glob.current_food_sum["fats"]) and \
                    float(glob.allfooditems[int(each.id)]["carbs"]) * 1 < glob.needed_macros[3] - float(
                glob.current_food_sum["carbs"]):
                if glob.allfooditems[int(each.id)]["pressed_amount"] > 0:
                    each._md_bg_color = [0.7, 0.7, 0, 0.7]
                else:
                    each._md_bg_color = [1, 1, 0, 0.7]
            else:
                each._md_bg_color = [1, 0, 0, 0.7]




    def add_forms(self):
        self.needed_list.bind(minimum_height=self.setter("height"))
        for meal in glob.allfooditems[MainApp.counter:]:
            row = BoxButton(orientation="horizontal", padding=[10,0,10,0],size_hint=[1, None], _md_bg_color=[1, 1, 1, .5],
                            id=str(glob.allfooditems.index(meal)))

            values = list(meal.values())
            bt0 = Label(text="Name\n" + values[0], font_size=16, size_hint=[0.4, 1], color=[0, 0, 0, 1], valign="middle")
            bt0.bind(size=bt0.setter('text_size'))
            bt1 = Label(text="kkal\n" + values[1], font_size=16, size_hint=[0.15, 1], color=[0, 0, 0, 1])
            bt2 = Label(text="proteins\n" + values[2], font_size=16, size_hint=[0.15, 1], color=[0, 0, 0, 1])
            bt3 = Label(text="fats\n" + values[3], font_size=16, size_hint=[0.15, 1], color=[0, 0, 0, 1])
            bt4 = Label(text="carbs\n" + values[4], font_size=16, size_hint=[0.15, 1], color=[0, 0, 0, 1])
            row.add_widget(bt0)
            row.add_widget(bt1)
            row.add_widget(bt2)
            row.add_widget(bt3)
            row.add_widget(bt4)
            self.needed_list.add_widget(row)
            if meal["pressed_amount"]>0:
                row.state = 'down'
            else:
                row.state = 'normal'
            MainApp.counter += 1
        for _ in range(2):
            row = BoxButton(orientation="horizontal", padding=[10, 0, 10, 0], size_hint=[1, None],
                            _md_bg_color=[1, 1, 1, .5])
            self.needed_list.add_widget(row)



class SettingsNavItem(MDBottomNavigationItem):
    def sumbit_profile_click(self, _age, _weight, _height, _gender):
        try:
            glob.user_profile["age"] = int(_age)
            glob.user_profile["weight"] = float(_weight)
            glob.user_profile["height"] = float(_height)
            glob.user_profile["male"] = bool(_gender=='m')
            self.errorText.color = [1, 1, 1, 0]
        except (ValueError, TypeError):
            self.errorText.color=[1,0,0,1]

class LoadingScreen(Screen):
    Builder.load_file("loading_screen.kv")


class MainApp(MDApp):
    counter = 0
    help_counter = 0
    Config.set('graphics', 'width', '360')
    Config.set('graphics', 'height', '640')
    global sm
    sm = ScreenManager()
    def on_start(self):
        Window.size = (360, 640)
        Clock.schedule_once(self.change_screen_to_main, 2)

    def on_stop(self):
        save_data([glob.user_profile, glob.allfooditems, glob.current_food_sum, glob.food_choices])
    def change_screen_to_main(self, dt):
        sm.current = 'FitnessApp'
        Window.size = (360, 640)
    def change_screen_to_loading(self, dt):
        sm.current = 'LoadingScreen'

    def end_day(self):
        glob.food_choices.append([])
        for meal in glob.allfooditems:
            if meal["pressed_amount"] > 0:
                glob.food_choices[-1].append(meal['name'])
                meal['pressed_amount'] = 0
        Clock.schedule_once(self.change_screen_to_loading, 1)
        Clock.schedule_once(self.change_screen_to_main, 3)
    def build(self):
       # self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.accent_palette = 'DeepPurple'
        #Window.clearcolor = (1,0,1,1)
        sm.add_widget(Fitnessapp())
        sm.add_widget(LoadingScreen())
        sm.current = "LoadingScreen"
        return sm


def calculate_def_macros(profile):
    stress_factor = 1
    if profile["male"]:
        def_calories = 5 + (10 * float(profile["weight"])) + (6.25 * float(profile["height"])) - (
                5 * float(profile["age"]))
        def_calories *= stress_factor
    else:
        def_calories = -161 + (10 * float(profile["weight"])) + (6.25 * float(profile["height"])) - (
                5 * float(profile["age"]))
        def_calories *= stress_factor
    def_calories = round(def_calories)
    def_proteins = round(def_calories * 0.25 / 4)
    def_fats = round(def_calories * 0.30 / 8)
    def_carbs = round(def_calories * 0.45 / 4)
    return [def_calories, def_proteins, def_fats, def_carbs]


# requiredMacros = {"calories": def_calories, "proteins": def_proteins, "fats": def_fats, "carbs": def_carbs}
if __name__ == '__main__':
    MainApp().run()
