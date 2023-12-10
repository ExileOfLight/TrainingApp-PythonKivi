import pickle

from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
from kivymd.app import MDApp
from kivymd.toast.kivytoast.kivytoast import toast
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.stacklayout import MDStackLayout

import globals as glob
from magic import apriori


def save_data(self):
    """Saves the data into a pickle file for reuse later."""
    pickle_data = self
    filename = "saved_data.pickle"
    pickle_out = open(filename, "wb")
    pickle.dump(pickle_data, pickle_out)
    pickle_out.close()


def load_data(self):
    """Loads the data from a pickle file and reads to the list"""
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
        data_saved = [{}, [], {}, [], []]
        try:
            load_data(data_saved)
            glob.user_profile = data_saved[0]
            glob.allfooditems = data_saved[1]
            glob.current_food_sum = data_saved[2]
            glob.food_choices = data_saved[3]
            glob.diet_plan = data_saved[4]
        except EOFError:
            print('Loading defaults')
        self.show_recommend()

    def on_pre_enter(self):
        Window.size = (360, 640)
        self.add_forms()

    def add_forms(self):
        allFood = glob.allfooditems
        self.foodMenuScreen.needed_list.clear_widgets()

        self.foodMenuScreen.needed_list.bind(minimum_height=self.setter("height"))
        for meal in allFood:
            row = ToggleFoodButton(orientation="horizontal", padding=[10, 0, 10, 0], size_hint=[1, None],
                                   _md_bg_color=[1, 1, 1, .5],
                                   id=str(allFood.index(meal)))

            values = list(meal.values())
            bt0 = Label(text="Name\n" + str(values[0]), font_size=16, size_hint=[0.3, 1], color=[0, 0, 0, 1],
                        valign="middle")
            bt0.bind(size=bt0.setter('text_size'))
            bt1 = Label(text="Kkal\n" + str(values[1]), font_size=16, size_hint=[0.15, 1], color=[0, 0, 0, 1])
            bt2 = Label(text="Proteins\n" + str(values[2]), font_size=16, size_hint=[0.15, 1], color=[0, 0, 0, 1])
            bt3 = Label(text="Fats\n" + str(values[3]), font_size=16, size_hint=[0.15, 1], color=[0, 0, 0, 1])
            bt4 = Label(text="Carbs\n" + str(values[4]), font_size=16, size_hint=[0.15, 1], color=[0, 0, 0, 1])
            bt5 = MDRaisedButton(font_size=16, size_hint=[0.1, 1], height="12dp")
            bt5.bind(on_release=self.foodMenuScreen.deleteItem)
            row.add_widget(bt0)
            row.add_widget(bt1)
            row.add_widget(bt2)
            row.add_widget(bt3)
            row.add_widget(bt4)
            row.add_widget(bt5)
            self.foodMenuScreen.needed_list.add_widget(row)
            if meal["pressed_amount"] > 0:
                row.state = 'down'
            else:
                row.state = 'normal'

    def submit_food_click(self):
        allFood = glob.allfooditems
        try:
            newDict = {"name": str(self.ids.name_input.text), "calories": int(self.ids.calories_input.text),
                       "proteins": int(self.ids.proteins_input.text), "fats": int(self.ids.fats_input.text),
                       "carbs": int(self.ids.carbs_input.text), "pressed_amount": 0}
            if newDict not in allFood:
                allFood.append(newDict)
            glob.allfooditems = allFood
            self.add_forms()
        except (ValueError, TypeError):
            toast("Please, fiil out all the fields")

    def show_recommend(self):
        glob.needed_macros = calculate_def_macros(glob.user_profile, glob.diet_plan)
        self.ids.calories_show.text = "kkal\n" + str(glob.current_food_sum["calories"]) + "/" + str(
            glob.needed_macros[0])
        self.ids.proteins_show.text = "proteins\n" + str(glob.current_food_sum["proteins"]) + "/" + str(
            glob.needed_macros[1])
        self.ids.fats_show.text = "fats\n" + str(glob.current_food_sum["fats"]) + "/" + str(glob.needed_macros[2])
        self.ids.carbs_show.text = "carbs\n" + str(glob.current_food_sum["carbs"]) + "/" + str(glob.needed_macros[3])
        # MainApp.stop(MainApp())


class FoodNavigationItem(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def deleteItem(self, dltButton):
        print(int(dltButton.parent.id))
        # Add counter
        glob.allfooditems.pop((int(dltButton.parent.id)))
        print(glob.allfooditems)
        dltButton.parent.parent.remove_widget(dltButton.parent)

    def food_help(self):
        allFood = glob.allfooditems
        for each in self.needed_list.children:
            print(int(each.id))
            print(allFood[-1 * (int(each.id) + 1)])
            if float(allFood[int(each.id)]
                     ["calories"]) * 3 < glob.needed_macros[0] and \
                    float(allFood[int(each.id)]["proteins"]) * 3 < glob.needed_macros[1] and \
                    float(allFood[int(each.id)]["fats"]) * 3 < glob.needed_macros[2] and \
                    float(allFood[int(each.id)]["carbs"]) * 3 < glob.needed_macros[3] and \
                    float(allFood[int(each.id)]["carbs"]) * 4 / float(
                allFood[int(each.id)]["calories"]) < 0.9:
                if allFood[int(each.id)]["pressed_amount"] > 0:
                    each._md_bg_color = [0.7, 0.5, 0.5, 0.8]
                else:
                    each._md_bg_color = [0, 1, 0, 0.5]
            elif float(allFood[int(each.id)]["calories"]) * 1 < glob.needed_macros[0] - float(
                    glob.current_food_sum["calories"]) and \
                    float(allFood[int(each.id)]["proteins"]) * 1 < glob.needed_macros[1] - float(
                glob.current_food_sum["proteins"]) and \
                    float(allFood[int(each.id)]["fats"]) * 1 < glob.needed_macros[2] - float(
                glob.current_food_sum["fats"]) and \
                    float(allFood[int(each.id)]["carbs"]) * 1 < glob.needed_macros[3] - float(
                glob.current_food_sum["carbs"]):
                if allFood[int(each.id)]["pressed_amount"] > 0:
                    each._md_bg_color = [0.7, 0.5, 0.5, 0.8]
                else:
                    each._md_bg_color = [1, 1, 0, 0.7]
            else:
                if allFood[int(each.id)]["pressed_amount"] > 0:
                    each._md_bg_color = [0.7, 0.5, 0.5, 0.8]
                else:
                    each._md_bg_color = [1, 0, 0, 0.7]

    def add_forms(self):
        allFood = glob.allfooditems
        self.needed_list.bind(minimum_height=self.setter("height"))
        for meal in allFood[MainApp.counter:]:
            row = ToggleFoodButton(orientation="horizontal", padding=[10, 0, 10, 0], size_hint=[1, None],
                                   _md_bg_color=[1, 1, 1, .5],
                                   id=str(allFood.index(meal)))

            values = list(meal.values())
            bt0 = Label(text="Name\n" + values[0], font_size=16, size_hint=[0.4, 1], color=[0, 0, 0, 1],
                        valign="middle")
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
            if meal["pressed_amount"] > 0:
                row.state = 'down'
            else:
                row.state = 'normal'
            MainApp.counter += 1
        for _ in range(2):
            row = ToggleFoodButton(orientation="horizontal", padding=[10, 0, 10, 0], size_hint=[1, None],
                                   _md_bg_color=[1, 1, 1, .5])
            self.needed_list.add_widget(row)


class SelectedFoods(MDLabel):
    def show_current(self):
        current_calories = glob.current_food_sum["calories"]
        current_proteins = glob.current_food_sum["proteins"]
        current_fats = glob.current_food_sum["fats"]
        current_carbs = glob.current_food_sum["carbs"]
        self.text = "kkal: " + str(current_calories) + "\nproteins: " + str(
            current_proteins) + "  fats: " + str(current_fats) + "  carbs: " + str(current_carbs)


class ToggleFoodButton(ToggleButtonBehavior, MDBoxLayout):
    def __init__(self, **kwargs):
        super(ToggleFoodButton, self).__init__(**kwargs)

    def change_current_food_sum(self, sign):
        allFood = glob.allfooditems
        current_calories = glob.current_food_sum["calories"]
        current_proteins = glob.current_food_sum["proteins"]
        current_fats = glob.current_food_sum["fats"]
        current_carbs = glob.current_food_sum["carbs"]

        current_calories += round(
            float(allFood[int(self.id)]["calories"]) * allFood[int(self.id)][
                "pressed_amount"] * sign)
        current_proteins += round(
            float(allFood[int(self.id)]["proteins"]) * allFood[int(self.id)][
                "pressed_amount"] * sign)
        current_fats += round(
            float(allFood[int(self.id)]["fats"]) * allFood[int(self.id)]["pressed_amount"] * sign)
        current_carbs += round(
            float(allFood[int(self.id)]["carbs"]) * allFood[int(self.id)]["pressed_amount"] * sign)

        glob.current_food_sum["calories"] = current_calories
        glob.current_food_sum["proteins"] = current_proteins
        glob.current_food_sum["fats"] = current_fats
        glob.current_food_sum["carbs"] = current_carbs

    def on_state(self, widget, value):
        if value == 'down':

            if glob.allfooditems[int(self.id)]["pressed_amount"] == 0:
                AmountAskPopup(widget=self).open()
            else:
                self.parent.parent.parent.parent.selected_foods.show_current()
            self._md_bg_color = [0.7, 0.5, 0.5, 0.8]

        else:
            self._md_bg_color = [1, 1, 1, .5]
            self.change_current_food_sum(-1)
            glob.allfooditems[int(self.id)]["pressed_amount"] = 0
            self.parent.parent.parent.parent.selected_foods.show_current()


class HelpButton(ToggleButton):
    def on_state(self, widget, value):
        allFood = glob.allfooditems
        # if self.state == 'down' else app.theme_cls.primary_light
        if value == 'down':
            self.parent.parent.food_help()
            self.call_apriori()
        else:
            self.text = "Помощь"
            for each in self.parent.parent.needed_list.children:
                if allFood[int(each.id)]['pressed_amount'] == 0:
                    each._md_bg_color = [1, 1, 1, 0.5]
                else:
                    each._md_bg_color = [0.7, 0.5, 0.5, 0.8]

        MainApp.help_counter += 1

    def call_apriori(self):
        allFood = glob.allfooditems
        result = apriori(glob.food_choices, 0.01, 0.01, 0.01, len(self.parent.parent.needed_list.children))
        current_pressed = set()
        competition = []
        for each in allFood:
            if each['pressed_amount'] > 0:
                current_pressed.add(each['name'])
        for rules_data in result:  # rules_data - [набор, поддержка набора, условие правила, достоверность правила, лифт правила]
            condition = rules_data[2].split(' ')
            condition = [name.replace('_', ' ') for name in condition]
            condition = set(condition)
            full_set = set(rules_data[0].split(' '))
            if not current_pressed.difference(condition):
                if rules_data[4] >= 1 and len(full_set) - len(condition) == 1:
                    competition.append(rules_data)
        if len(competition) > 0:
            competitionSorted = sorted(competition, key=lambda x: x[3] + x[4])
            best_rule = competitionSorted.pop()
            condition = set(best_rule[2].split(' '))
            full_set = set(best_rule[0].split(' '))
            diff = full_set.difference(condition)
            self.text = str(diff.pop())


class AmountAskPopup(Popup):
    widget = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_popup_to_calcs(self, text):
        try:
            glob.allfooditems[int(self.widget.id)]["pressed_amount"] = float(text)
            self.widget.change_current_food_sum(1)
            self.widget.parent.parent.parent.parent.selected_foods.show_current()
            self.dismiss()
        except ValueError:
            toast("Enter a valid number (rational)")


class SettingsNavItem(MDBottomNavigationItem):
    def on_enter(self, *args):
        self.current_age.text = str(glob.user_profile["age"])
        self.current_height.text = str(glob.user_profile["height"])
        self.current_weight.text = str(glob.user_profile["weight"])
        self.current_gender.text = str(glob.user_profile["gender"])

    def submit_profile_click(self, _age, _weight, _height, _gender, _diet):
        try:
            glob.user_profile["age"] = int(_age)
            glob.user_profile["weight"] = int(_weight)
            glob.user_profile["height"] = int(_height)
            glob.user_profile["gender"] = _gender
            for child in _diet.children:
                if child.state == 'down':
                    if child.text == "Bulk":
                        glob.diet_plan["deficit"] = -300
                    elif child.text == "Deficit":
                        glob.diet_plan["deficit"] = 300
                    else:
                        glob.diet_plan["deficit"] = 0

            # self.parent.parent.parent.show_recommend()
            save_data([glob.user_profile, glob.allfooditems, glob.current_food_sum, glob.food_choices, glob.diet_plan])
        except (ValueError, TypeError):
            toast("Please fill out all the fields")


class ButtonsDeficitChoice(MDStackLayout):
    def on_button_pressed(self, button):
        for child in self.children:
            if child != button:
                child.md_bg_color = [0, 0, 0.2, 0.8]
                child.state = 'normal'
            else:
                child.md_bg_color = [0, 0, 1, 1]
                child.state = 'down'


class LoadingScreen(Screen):
    Builder.load_file("loading_screen.kv")


class MainApp(MDApp):
    help_counter = 0
    Config.set('graphics', 'width', '360')
    Config.set('graphics', 'height', '640')
    global sm
    sm = ScreenManager()

    def on_start(self):
        Clock.schedule_once(self.change_screen_to_main, 2)

    def on_stop(self):
        save_data([glob.user_profile, glob.allfooditems, glob.current_food_sum, glob.food_choices, glob.diet_plan])

    def change_screen_to_main(self, dt):
        sm.current = 'FitnessApp'

    def change_screen_to_loading(self, dt):
        sm.current = 'LoadingScreen'

    def end_day(self):

        allFood = glob.allfooditems
        glob.food_choices.append([])
        for meal in allFood:
            if meal["pressed_amount"] > 0:
                glob.food_choices[-1].append(meal['name'])
                meal['pressed_amount'] = 0
        glob.current_food_sum = {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
        save_data([glob.user_profile, glob.allfooditems, glob.current_food_sum, glob.food_choices, glob.diet_plan])
        sm.clear_widgets()
        sm.add_widget(Fitnessapp())
        sm.add_widget(LoadingScreen())
        sm.current = "LoadingScreen"
        Clock.schedule_once(self.change_screen_to_main, 2)

    def build(self):
        # self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.accent_palette = 'DeepPurple'
        # Window.clearcolor = (1,0,1,1)
        sm.add_widget(Fitnessapp())
        sm.add_widget(LoadingScreen())
        sm.current = "LoadingScreen"
        return sm


def calculate_def_macros(profile, diet_plan):
    protein_perct = diet_plan["protein"]
    fat_perct = diet_plan["fat"]
    carb_perct = diet_plan["carb"]
    deficit = diet_plan["deficit"]
    stress_factor = 1
    if profile["gender"] == "m":
        def_calories = 5 + (10 * float(profile["weight"])) + (6.25 * float(profile["height"])) - (
                5 * float(profile["age"]))
    else:
        def_calories = -161 + (10 * float(profile["weight"])) + (6.25 * float(profile["height"])) - (
                5 * float(profile["age"]))
    def_calories *= stress_factor
    def_calories = round(def_calories) - deficit
    def_proteins = round(def_calories * protein_perct / 4)
    def_fats = round(def_calories * fat_perct / 8)
    def_carbs = round(def_calories * carb_perct / 4)
    return [def_calories, def_proteins, def_fats, def_carbs]


# requiredMacros = {"calories": def_calories, "proteins": def_proteins, "fats": def_fats, "carbs": def_carbs}
if __name__ == '__main__':
    MainApp().run()
