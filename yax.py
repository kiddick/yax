# -*- coding: utf-8 -*-

import requests
import lxml.html
import os
import webbrowser
from collections import Mapping, OrderedDict
import json

import spoilog


class Entity(object):

    def __init__(self, xpath, element, parent=None):
        self.xpath = xpath
        self.parent = parent
        self.element = element


def keypaths(nested):
    for key, value in nested.iteritems():
        if isinstance(value, Mapping) and value:
            for subkey, subvalue in keypaths(value):
                yield [key] + subkey, subvalue
        else:
            yield [key], value


def get_from_dict(dataDict, mapList):
    return reduce(lambda d, k: d[k], mapList, dataDict)


def push(el, store):
    if not el.parent:
        store[(el.xpath, pretty(el.element))] = OrderedDict()
    else:
        for kp in keypaths(store):
            if el.parent.xpath in (x[0] for x in kp[0]):
                if isinstance(el.element, lxml.html.HtmlElement):
                    foormatme = pretty(el.element)
                else:
                    foormatme = el.element.encode('utf-8')
                get_from_dict(store, kp[0][:[x[0] for x in kp[0]].index(
                    el.parent.xpath) + 1])[(el.xpath, foormatme)] = OrderedDict()


def entity_factory(path=None, parent=None, d=None, single=False, note=None, text=None):
    if text:
        return Entity(path, text, parent)
    elif parent:
        raw = parent.element.xpath(path)
    elif d:
        raw = d.xpath(path)
    else:
        raise
    if single and text:
        return Entity(path, raw, parent)
    if single:
        return Entity(path, raw[0], parent)
    else:
        return [Entity(path, el, parent) for el in raw]


def save(data, fname, ext, d):
    ed = {
        'h': 'html',
        't': 'txt'
    }
    with open(os.path.join(os.getcwd(), fname + '.' + ed[ext]), d) as f:
        f.write(data)


def pretty(data):
    # return lxml.etree.tostring(data, encoding='utf-8', pretty_print=True)
    return lxml.etree.tostring(data, pretty_print=True)


# class Word(object):
    # def __init__(self,)

class YaX(object):

    def __init__(self, expr):
        self.expr = expr
        self.url = 'https://slovari.yandex.ru/' + self.expr + '/перевод/'
        # print requests.get(self.url).encoding
        self.doc = lxml.html.fromstring(requests.get(self.url).content)

    def parse(self):
        XP = {
            'tr_tree': '//div[@class="b-translation__card b-translation__card_examples_three"]',
            'tr_groups': './/div[@class="b-translation__group"]',
            'last_tr_group': './/div[@class="b-translation__group b-translation__group_last_yes"]',
            'group_title': './/h2[@class="b-translation__group-title"]',
            'tr_entries': './/li[@class="b-translation__entry"]',
            'tr_entry_hidden': './/li[@class="b-translation__entry b-translation__entry_hidden_yes"]',
            'tr_examples': './/div[@class="b-translation__examples"]',
            'tr_example': './/div[@class="b-translation__example"]',
            'tr_example_hidden': './/div[@class="b-translation__example b-translation__example_type_hidden b-translation__example_hidden_yes"]',
            'translation_text': './/div[@class="b-translation__translation"]//span[@class="b-translation__text"]|.//div[@class="b-translation__translation"]//span[@class="b-translation__comment"]',
        }
        word = OrderedDict()
        output = OrderedDict()
        # tree = self.cut_tr_tree(self.doc, singe=True)  # get main tree
        tree = entity_factory(path=XP['tr_tree'], d=self.doc, single=True)
        if tree:
            # push(tree, output)
            groups = entity_factory(path=XP['tr_groups'], parent=tree)
            groups.append(
                entity_factory(
                    path=XP['last_tr_group'], parent=tree, single=True))
            for group in groups:
                # push(group, output)
                try:
                    group_title = entity_factory(
                        path=XP['group_title'], parent=group, single=True)
                    pspeech = group_title.element.get('id')
                except IndexError:
                    pspeech = 'misc'
                # pspeech = group_title.element.get('id')
                word[pspeech] = dict()
                # push(group_title, output)
                entries = entity_factory(path=XP['tr_entries'], parent=group)
                entries += entity_factory(
                    path=XP['tr_entry_hidden'], parent=group)
                word[pspeech]['translations'] = OrderedDict()
                # word[pspeech]['examples'] = []
                for entry in entries:
                    # push(entry, output)
                    translations = entity_factory(
                        path=XP['translation_text'], parent=entry)
                    # for translation in translations:
                        # push(translation, output)
                    trn = (''.join(
                        [translation.element.text for translation
                         in translations]
                    ).encode('utf-8'))
                    word[pspeech]['translations'][trn] = []
                    # print 'len', len(''.join([translation.element.text for translation in translations]).encode('utf-8'))
                    # trn = ''.join([translation.element.text for translation in translations])
                    # if trn:
                    # push(entity_factory(
                    #     text=''.join([translation.element.text for translation in translations]), parent=entry, single=True),
                    #     output
                    # )
                    examples = entity_factory(
                        path=XP['tr_examples'], parent=entry)
                    for example in examples:
                        # push(example, output)
                        _examples = entity_factory(
                            path=XP['tr_example'], parent=example)
                        _examples += entity_factory(
                            path=XP['tr_example_hidden'], parent=example)
                        for xmp in _examples:
                            word[pspeech]['translations'][trn].append(
                                xmp.element.text_content().encode('utf-8'))
        jword = json.dumps(word, indent=4, ensure_ascii=False)
        with open('word.txt', 'w') as wrd:
            wrd.write(jword)
        spoilog.render('real.html', output)


# yx = YaX('test')
yx = YaX('test')
# yx = YaX('future')
# yx = YaX('know')
# yx = YaX('wolf')
# yx = YaX('word')
yx.parse()
