from . import account, investment, withdrawal

import html as html_cvt
from bs4 import BeautifulSoup
from bs4.element import Comment, NavigableString, Tag
import re
import cloudscraper

class EasyProject:
    def __init__(self, **kwargs):
        self.timeout = 30
        self.url = None
        self.account = None
        self.investment = None
        self.withdrawal = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_info_project(self):
        if(self.url is None or self.account is None or self.investment is None or self.withdrawal is None):
            return
        scraper = cloudscraper.create_scraper()
        html = scraper.get(self.url, timeout=self.timeout).text
        html = html_cvt.unescape(html)
        soup = BeautifulSoup(html, "lxml")

        texts = soup.findAll(text=True)
        visible_texts = filter(self._tag_visible, texts)

        visible_texts = [item for item in visible_texts if item is not None]
        visible_texts = [item for item in visible_texts if self.check_condition(item)]

        ricker_arr = []
        for item in visible_texts:
            ricker_arr += self.ricker(item)
        ricker_arr = [item for item in ricker_arr if item is not None]
        visible_texts += ricker_arr
        
        total_investments = self._check_in_list(visible_texts, self.investment)
        total_paid_outs = self._check_in_list(visible_texts, self.withdrawal)
        total_members = self._check_in_list(visible_texts, self.account, int)
        if int(total_investments) == -1 and int(total_paid_outs) == -1:
            pass
        else:
            if abs(total_investments - total_paid_outs) <= 0.0001:
                total_investments = -1
                total_paid_outs = -1
            elif total_paid_outs != 0 and total_investments/total_paid_outs > 10000:
                total_investments = -1
                total_paid_outs = -1
        return total_investments, total_paid_outs, total_members

    def preprocess_data(self, data):
        data = data.split("+")[0]
        def remove_at(i, s):
            return s[:i] + s[i+1:]
    
        def clear_text(s):
            if '.' in s:
                start = s.index('.')
                while True:
                    try:
                        index = s.index('.', start + 1)
                        s = remove_at(index, s)
                    except:
                        break
            return s
        return clear_text(re.sub(r"[^0-9\.]", "", data))

    def check_condition(self, txt):
        check = txt
        if isinstance(txt, Tag):
            check = txt.text
        check = check.strip().replace("\n", "").replace("\t", "").replace("  ", "").strip()
        return len(check) <= 25 and (len(check) >= 4 or self._check_num(check, float) is not None)

    def ricker(self, element, lv=1):
        if lv >= 3:
            return []
        if element.parent is not None:
            if self.check_condition(element.parent):
                return [element.parent] + self.ricker(element.parent, lv=lv+1)
        return []

    def _tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def _check_num(self, s, type):
        try:
            return type(float(s))
        except:
            pass

    def _get_parent_up_lever(self, children, num):
        current = children.parent
        for _ in range(num):
            current = current.parent
        return current.children

    def check_in_list(self, items, lst):
        result = []
        for item in items:
            check = item
            if isinstance(item, Tag):
                check = item.text
            
            for idx, word in enumerate(lst):
                if word.lower() in check.lower() or word.lower().replace(" ", "") in check.lower():
                    result.append((idx, item))
                    break

        result = sorted(result, key=lambda kv: kv[0])
        result = [item[1] for item in result]
        return result    
    
    def _check_in_list(self, items, lst, type=float):
        result = self.check_in_list(items, lst)

        for item in result:
            for i in range(3):
                for children in self._get_parent_up_lever(item, i):
                    check = children
                    if isinstance(children, Tag):
                        check = children.text
                    if self.check_condition(check):
                        txt = self.preprocess_data(check)
                        temp = self._check_num(txt, type)
                        if temp is not None:
                            return temp
        return type(-1)

def check(url: str):
    return EasyProject(url=url, account=account, investment=investment, withdrawal=withdrawal).get_info_project()