import re
import json
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import collections
from operator import itemgetter

sns.set(style='whitegrid')

class DataVisualizer:
    def __init__(self, data_list):
        self.data_list = data_list
        self.cities = []
        self.oblasts = []
        self.schools = []
        self.types = []
        self.usages = []
        self.sentiments = []
        self.get_city2oblast()
        self.process_data()
        self.visualize()

    def get_city2oblast(self):
        df = pd.read_html('https://uk.wikipedia.org/wiki/%D0%9C%D1%96%D1%81%D1%82%D0%B0_%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D0%B8_(%D0%B7%D0%B0_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D1%96%D1%82%D0%BE%D0%BC)')[0]
        self.city2oblast = {row['Місто']: row['Область, АРК'] for i, row in df.iterrows()}

    def process_data(self):
        for entry in self.data_list:
            items = entry.split(' | ')
            if len(items)<6:
                continue
            else:
                city = items[0].split(':')[-1].strip()
                oblast = items[1].split(':')[-1].strip()
                if city == 'Київ':
                    oblast = 'Київ'
                if oblast=='-':
                    if city in self.city2oblast:
                        oblast = self.city2oblast[city]
                
                oblast = re.sub('область', '', oblast).strip()
                
                raw_school = items[2].split(':')[-1].strip()
                if city!='-' and oblast!='-':
                    school = f'{city}, {oblast}, {raw_school}'
                else:
                    school = '-'

                jtype = items[3].split(':')[-1].strip()
                jtype = re.sub('\"', '', jtype).lower()

                if jtype in {'щоденник', 'електронний щоденник', 'електронний'}:
                    jtype = '-'
                elif jtype == 'human':
                    jtype = 'human.ua'

                raw_usage = items[4].split(':')[-1].strip()
                usage = re.search('ніколи|періодично|завжди', raw_usage)
                if usage:
                    usage = usage.group(0)
                else:
                    usage = '-'
                if usage == '-':
                    usage = 'ніколи'

                raw_sentiment = items[5].split(':')[-1].strip()
                sentiment = re.search('нейтральний|позитивний|негативний', raw_sentiment)
                if sentiment:
                    sentiment = sentiment.group(0)
                else:
                    sentiment = '-'

                self.cities.append(city)
                self.oblasts.append(oblast)
                self.schools.append(school)
                self.types.append(jtype)
                self.usages.append(usage)
                self.sentiments.append(sentiment)

    def visualize_bar(self, data, title, xn, yn, name, n=10):
        plt.clf()
        plt.figure(figsize=(12, 8))

        obj_counts = collections.Counter(data)
        del obj_counts['-']

        top_objs = sorted(obj_counts.items(), key=itemgetter(1), reverse=True)[:n]
        names, values = zip(*top_objs)

        plt.bar(names, values)

        plt.title(title, fontsize=20)
        plt.xlabel(xn, fontsize=14)
        plt.ylabel(yn, fontsize=14)
        plt.xticks(fontsize=12, rotation=45)
        plt.yticks(fontsize=12)

        for index, value in enumerate(values):
            plt.text(index, value + 0.5, str(value), ha='center', fontsize=12, color='black')

        plt.savefig(f'imgs/{name}.png', bbox_inches='tight')

    def visualize_double_bar(self, data, title, xn, yn, name, n=10):
        plt.clf()
        plt.figure(figsize=(12, 8))
    
        sentiments = set(self.sentiments)
        sentiments.remove('-')

        sentiment2data = {sentiment: [] for sentiment in sentiments}
        for sentiment, entry in zip(self.sentiments, data):
            if sentiment!='-':
                sentiment2data[sentiment].append(entry)

        obj_counts = collections.Counter(data)
        del obj_counts['-']

        top_objs = sorted(obj_counts.items(), key=itemgetter(1), reverse=True)[:n]
        names, values = zip(*top_objs)

        X = list(names)
        X_axis = np.arange(len(X))
        c = 0
        width = 0.3
        for sentiment, data in sentiment2data.items():
            obj_counts = collections.Counter(data)
            del obj_counts['-']

            if not names:
                top_objs = sorted(obj_counts.items(), key=itemgetter(1), reverse=True)[:n]
                names, values = zip(*top_objs)

            else:
                values = []
                for iname in names:
                    if iname in obj_counts:
                        values.append(obj_counts[iname])
                    else:
                        values.append(0)

            plt.bar(X_axis+width*c, values, width, label = sentiment)
            c+=1

        plt.title(title, fontsize=20)
        plt.xlabel(xn, fontsize=14)
        plt.ylabel(yn, fontsize=14)
        plt.xticks(X_axis, X)
        plt.xticks(fontsize=12, rotation=45)
        plt.yticks(fontsize=12)
        plt.legend()

        plt.savefig(f'imgs/{name}.png', bbox_inches='tight')

    def visualize_pie(self, data, title, name):
        plt.clf()
        plt.figure(figsize=(12, 8))

        obj_counts = collections.Counter(data)
        del obj_counts['-']

        sorted_data = sorted(obj_counts.items(), 
                                key= lambda key_value: key_value[1],
                                reverse=True)

        colors = ["#00ebc1", "#00b8ba", "#0085b4", "#0051ad", "#001ea6"]

        labels = [key_value_tuple[0] for key_value_tuple in sorted_data]
        data = [key_value_tuple[1] for key_value_tuple in sorted_data]

        total = sum(data)
        percentages = ["{0:.1%}".format(value / total) for value in data]

        plt.pie(data,labels=percentages,startangle=90,counterclock=False,
            colors=colors,textprops={"ha":"center"},labeldistance=1.15)
        plt.legend(labels=labels,loc=(1.02,0.25))
        plt.tight_layout(pad=3)
        plt.title(title)
        plt.savefig(f'imgs/{name}.png', bbox_inches='tight')

    def visualize(self):
        title = 'Топ 10 міст за кількістю коментарів'
        xn = 'Місто'
        yn = 'Кількість коментарів'
        self.visualize_bar(self.cities, title, xn, yn, 'top_cities', n=10)

        title = 'Топ 10 областей за кількістю коментарів'
        xn = 'Область'
        yn = 'Кількість коментарів'
        self.visualize_bar(self.oblasts, title, xn, yn, 'top_oblasts', n=10)

        title = 'Топ 10 цифрових щоденників за використанням'
        xn = 'Цифровий щоденник'
        yn = 'Кількість згадуваннь'
        self.visualize_bar(self.types, title, xn, yn, 'top_digital_journals', n=10)

        title = "Відношення до ідеї використання цифрових щоденників"
        self.visualize_pie(self.sentiments, title, 'sentiments')

        title = "Рівень використання цифрових щоденників"
        self.visualize_pie(self.usages, title, 'usages')

        title = "Відгуки по областям"
        xn = 'Область'
        yn = 'Кількість коментів'
        self.visualize_double_bar(self.oblasts, title, xn, yn, 'oblasts_sentiments')

        title = "Відгуки по цифровим щоденникам"
        xn = 'Щоденник'
        yn = 'Кількість коментів'
        self.visualize_double_bar(self.types, title, xn, yn, 'digital_journals_sentiments')


if __name__ == '__main__':
    with open('data/responses.json', 'r') as f:
        data_list = json.load(f)['responses']
    
    visualizer = DataVisualizer(data_list)