from html.parser import HTMLParser


class EDEFuzzDOM():
    def __init__(self, tag="", parent=None):
        self.tag = tag
        self.parent = parent
        self.attr = {}
        self.content = []
        self.attr_ignore_all = False
        self.attr_ignore_list = set() # stores "key" of attributes to be ignored within attr
        self.content_ignore_all = False
        self.content_ignore_list = set() # stores index of elements to be ignored within content
        
    
    def set_tag(self, tag):
        self.tag = tag
    
    def set_attr(self, attrs):
        for key, value in attrs:
            self.attr[key] = value
    
    def add_content(self, content):
        self.content.append(content)
    
    def __str__(self):
        result = self.tag + "\n"
        for item in self.attr:
            result += item + str(self.attr[item]) + "\n"
        for item in self.content:
            result += str(item) + isinstance(item, str) * "\n"
        return result
    
    def mark_uncommon(self, DOM):
        if not isinstance(DOM, EDEFuzzDOM):
            raise Exception("A non EDEFuzzDOM object received by mark_uncommon: " + str(another_DOM))
        if self.tag != DOM.tag:
            raise Exception("Two baseline DOMs are structurally different (tag name). There might be issue in test execution, or EDEFuzz does not work on this target. ")
        if len(self.attr) == len(DOM.attr):
            for key in self.attr:
                if key in DOM.attr:
                    if self.attr[key] == DOM.attr[key]:
                        continue
                self.attr_ignore_list.add(key)
        else: # if another baseline DOM has different number of attributes
            raise Exception("Two baseline DOMs are structurally different (number of attributes). There might be issue in test execution, or EDEFuzz does not work on this target. ")
            self.attr_ignore_all = True
        if len(self.content) == len(DOM.content):
            for i in range(len(self.content)):
                if isinstance(self.content[i], EDEFuzzDOM) and isinstance(DOM.content[i], EDEFuzzDOM):
                    self.content[i].mark_uncommon(DOM.content[i])
                elif self.content[i] != DOM.content[i]:
                    self.content_ignore_list.add(i)
        else: # number of elements within this DOM object is different
            raise Exception("Two baseline DOMs are structurally different (number of elements). There might be issue in test execution, or EDEFuzz does not work on this target. ")
            self.content_ignore_all = True
    
    def __eq__(self, DOM):
        if isinstance(DOM, EDEFuzzDOM):
            # tag name must match
            if self.tag != DOM.tag:
                return False
            # if we need to compare attributes
            if self.attr_ignore_all == False:
                # if number of attributes different, return False
                if len(self.attr) != len(DOM.attr):
                    return False
                # compare each non-ignored attributes
                for key in self.attr:
                    if key in self.attr_ignore_list:
                        continue
                    if key not in DOM.attr:
                        return False
                    if self.attr[key] != DOM.attr[key]:
                        return False
            # if we need to compare contents within this DOM
            if self.content_ignore_all == False:
                # if number of elements different, return False
                if len(self.content) != len(DOM.content):
                    return False
                for i in range(len(self.content)):
                    if i in self.content_ignore_list:
                        continue
                    if self.content[i] != DOM.content[i]:
                        return False
            return True
        return False
        
        

class EDEFuzzHTMLParser(HTMLParser):
    def __init__(self):
        self.dom = EDEFuzzDOM("edefuzz_root")
        self.current = self.dom
        super().__init__()
        
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        t = EDEFuzzDOM(tag, self.current)
        t.set_attr(attrs)
        self.current.add_content(t)
        self.current = t

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        self.current = self.current.parent
    
    def handle_startendtag(self, tag, attrs):
        #print("Encountered a startend tag:", tag)
        t = EDEFuzzDOM(tag, self.current)
        t.set_attr(attrs)
        self.current.add_content(t)

    def handle_data(self, data):
        #print("Encountered some data  :", data)
        self.current.add_content(data)



if __name__ == "__main__":
    parser1 = EDEFuzzHTMLParser()
    parser1.feed('''<div data-automation="find-in-store" id="product-details-accordion-find-in-store-accordion-id" class="css-1uz161o"><h2><button aria-expanded="true" data-automation="find-in-store-button" class="css-1jjrg5s"><span class="css-uszmbf"><span id="find-in-store-accordion" tabindex="-1" data-automation="find-in-store-accordion-title">Find in store </span><svg width="24px" height="24px" viewBox="0 0 24 24" focusable="false" data-automation="add-remove"><g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="square"><g id="Remove" stroke="currentColor"><path vector-effect="non-scaling-stroke" d="M2.5,12.5 L21.5262976,12.5" id="Line-Copy"></path></g></g></svg></span></button></h2><div class="description" data-automation="in-store-stock-check"><div class="css-1fttcpj"><form data-automation="find-a-store-form" autocomplete="off" novalidate="" class="css-1fttcpj"><label for="find-a-store-text-input" class="css-1y459fh">enter a postcode</label><div class="css-15xwm00"><input id="find-a-store-text-input" type="text" data-automation="find-a-store-text-input" placeholder="Postcode" name="postcode" aria-labelledby="find-in-store-accordion find-a-store-text-input" class="css-sthr2v" value="3000"><button type="button" aria-label="use current location" class="css-1b4zdiu"><svg width="24px" height="24px" viewBox="0 0 24 24" fill="none" focusable="false"><circle vector-effect="non-scaling-stroke" cx="12" cy="12" r="2.5" stroke="currentColor"></circle><circle vector-effect="non-scaling-stroke" cx="12" cy="12" r="8" stroke="currentColor"></circle><path vector-effect="non-scaling-stroke" d="M12 4L12 0" stroke="currentColor"></path><path vector-effect="non-scaling-stroke" d="M12 24L12 20" stroke="currentColor"></path><line vector-effect="non-scaling-stroke" x1="20" y1="12" x2="24" y2="12" stroke="currentColor"></line><line vector-effect="non-scaling-stroke" y1="12" x2="4" y2="12" stroke="currentColor"></line></svg></button></div><input type="submit" data-automation="find-store" class="css-xrpxbx" value="Find stores"></form><div data-automation="find-a-store-results"><ol><li data-automation="bestLocation" class="css-1w6rldw"><span class="screen-reader-text" data-focus="to-focus" tabindex="-1">Highpoint 10 kilometres away In Stock</span><div aria-hidden="true" class="css-1gvk5ri"><div class="css-hcxeft"><a href="/store-locator/highpoint-victoria" id="store-Highpoint" data-automation="store-name" class="css-1p01ot7">Highpoint</a><span aria-describedby="store-Highpoint" data-automation="store-distance" class="css-kz9uiq"><span aria-hidden="true">10 km</span></span></div><div><span aria-describedby="store-Highpoint" data-automation="store-stock-level" class="css-1pa8ldy">In Stock</span></div></div></li></ol><p data-automation="bestLocationNote" class="css-5fj0jf">Order online now and collect at the store</p><div class="css-18vag0t"><button data-automation="more-stores" aria-expanded="false" class="css-j14voe">More stores around '3000'<svg class="css-vhd608 down" width="16px" height="16px" viewBox="0 0 24 24" focusable="false" aria-hidden="true"><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="square"><g stroke="currentColor" stroke-width="1.21428571"><polyline vector-effect="non-scaling-stroke" points="8 3.29999995 16.8163452 11.8633058 8 20.5598266"></polyline></g></g></svg></button></div><ol data-automation="location-list" aria-expanded="false" aria-hidden="true" class="css-43f66w"></ol><div data-automation="cc-indicative-availability" class="css-1330ege"><span>Indicative availability as of 21/09/2022 12:45</span></div></div></div></div></div>''')
    DOM1 = parser1.dom
    
    parser2 = EDEFuzzHTMLParser()
    parser2.feed('''<div data-automation="find-in-store" id="product-details-accordion-find-in-store-accordion-id" class="css-1uz161o"><h2><button aria-expanded="true" data-automation="find-in-store-button" class="css-1jjrg5s"><span class="css-uszmbf"><span id="find-in-store-accordion" tabindex="-1" data-automation="find-in-store-accordion-title">Find in store </span><svg width="24px" height="24px" viewBox="0 0 24 24" focusable="false" data-automation="add-remove"><g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="square"><g id="Remove" stroke="currentColor"><path vector-effect="non-scaling-stroke" d="M2.5,12.5 L21.5262976,12.5" id="Line-Copy"></path></g></g></svg></span></button></h2><div class="description" data-automation="in-store-stock-check"><div class="css-1fttcpj"><form data-automation="find-a-store-form" autocomplete="off" novalidate="" class="css-1fttcpj"><label for="find-a-store-text-input" class="css-1y459fh">enter a postcode</label><div class="css-15xwm00"><input id="find-a-store-text-input" type="text" data-automation="find-a-store-text-input" placeholder="Postcode" name="postcode" aria-labelledby="find-in-store-accordion find-a-store-text-input" class="css-sthr2v" value="3000"><button type="button" aria-label="use current location" class="css-1b4zdiu"><svg width="24px" height="24px" viewBox="0 0 24 24" fill="none" focusable="false"><circle vector-effect="non-scaling-stroke" cx="12" cy="12" r="2.5" stroke="currentColor"></circle><circle vector-effect="non-scaling-stroke" cx="12" cy="12" r="8" stroke="currentColor"></circle><path vector-effect="non-scaling-stroke" d="M12 4L12 0" stroke="currentColor"></path><path vector-effect="non-scaling-stroke" d="M12 24L12 20" stroke="currentColor"></path><line vector-effect="non-scaling-stroke" x1="20" y1="12" x2="24" y2="12" stroke="currentColor"></line><line vector-effect="non-scaling-stroke" y1="12" x2="4" y2="12" stroke="currentColor"></line></svg></button></div><input type="submit" data-automation="find-store" class="css-xrpxbx" value="Find stores"></form><div data-automation="find-a-store-results"><ol><li data-automation="bestLocation" class="css-1w6rldw"><span class="screen-reader-text" data-focus="to-focus" tabindex="-1">Highpoint 10 kilometres away In Stock</span><div aria-hidden="true" class="css-1gvk5ri"><div class="css-hcxeft"><a href="/store-locator/highpoint-victoria" id="store-Highpoint" data-automation="store-name" class="css-1p01ot7">Highpoint</a><span aria-describedby="store-Highpoint" data-automation="store-distance" class="css-kz9uiq"><span aria-hidden="true">10 km</span></span></div><div><span aria-describedby="store-Highpoint" data-automation="store-stock-level" class="css-1pa8ldy">In Stock</span></div></div></li></ol><p data-automation="bestLocationNote" class="css-5fj0jf">Order online now and collect at the store</p><div class="css-18vag0t"><button data-automation="more-stores" aria-expanded="false" class="css-j14voe">More stores around '3000'<svg class="css-vhd608 down" width="16px" height="16px" viewBox="0 0 24 24" focusable="false" aria-hidden="true"><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="square"><g stroke="currentColor" stroke-width="1.21428571"><polyline vector-effect="non-scaling-stroke" points="8 3.29999995 16.8163452 11.8633058 8 20.5598266"></polyline></g></g></svg></button></div><ol data-automation="location-list" aria-expanded="false" aria-hidden="true" class="css-43f66w"></ol><div data-automation="cc-indicative-availability" class="css-1330ege"><span>Indicative availability as of 21/09/2022 22:22</span></div></div></div></div></div>''')
    DOM2 = parser2.dom
    
    parser3 = EDEFuzzHTMLParser()
    parser3.feed('''<div data-automation="find-in-store" id="product-details-accordion-find-in-store-accordion-id" class="css-1uz161o"><h2><button aria-expanded="true" data-automation="find-in-store-button" class="css-1jjrg5s"><span class="css-uszmbf"><span id="find-in-store-accordion" tabindex="-1" data-automation="find-in-store-accordion-title">Find in store </span><svg width="24px" height="24px" viewBox="0 0 24 24" focusable="false" data-automation="add-remove"><g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="square"><g id="Remove" stroke="currentColor"><path vector-effect="non-scaling-stroke" d="M2.5,12.5 L21.5262976,12.5" id="Line-Copy"></path></g></g></svg></span></button></h2><div class="description" data-automation="in-store-stock-check"><div class="css-1fttcpj"><form data-automation="find-a-store-form" autocomplete="off" novalidate="" class="css-1fttcpj"><label for="find-a-store-text-input" class="css-1y459fh">enter a postcode</label><div class="css-15xwm00"><input id="find-a-store-text-input" type="text" data-automation="find-a-store-text-input" placeholder="Postcode" name="postcode" aria-labelledby="find-in-store-accordion find-a-store-text-input" class="css-sthr2v" value="3000"><button type="button" aria-label="use current location" class="css-1b4zdiu"><svg width="24px" height="24px" viewBox="0 0 24 24" fill="none" focusable="false"><circle vector-effect="non-scaling-stroke" cx="12" cy="12" r="2.5" stroke="currentColor"></circle><circle vector-effect="non-scaling-stroke" cx="12" cy="12" r="8" stroke="currentColor"></circle><path vector-effect="non-scaling-stroke" d="M12 4L12 0" stroke="currentColor"></path><path vector-effect="non-scaling-stroke" d="M12 24L12 20" stroke="currentColor"></path><line vector-effect="non-scaling-stroke" x1="20" y1="12" x2="24" y2="12" stroke="currentColor"></line><line vector-effect="non-scaling-stroke" y1="12" x2="4" y2="12" stroke="currentColor"></line></svg></button></div><input type="submit" data-automation="find-store" class="css-xrpxbx" value="Find stores"></form><div data-automation="find-a-store-results"><ol><li data-automation="bestLocation" class="css-1w6rldw"><span class="screen-reader-text" data-focus="to-focus" tabindex="-1">Highpoint 10 kilometres away In Stock</span><div aria-hidden="true" class="css-1gvk5ri"><div class="css-hcxeft"><a href="/store-locator/highpoint-victoria" id="store-Highpoint" data-automation="store-name" class="css-1p01ot7">Highpoint</a><span aria-describedby="store-Highpoint" data-automation="store-distance" class="css-kz9uiq"><span aria-hidden="true">10 km</span></span></div><div><span aria-describedby="store-Highpoint" data-automation="store-stock-level" class="css-1pa8ldy">In Stock</span></div></div></li></ol><p data-automation="bestLocationNote" class="css-5fj0jf">Order online now and collect at the store</p><div class="css-18vag0t"><button data-automation="more-stores" aria-expanded="false" class="css-j14voe">More stores around '3000'<svg class="css-vhd608 down" width="16px" height="16px" viewBox="0 0 24 24" focusable="false" aria-hidden="true"><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="square"><g stroke="currentColor" stroke-width="1.21428571"><polyline vector-effect="non-scaling-stroke" points="8 3.29999995 16.8163452 11.8633058 8 20.5598266"></polyline></g></g></svg></button></div><ol data-automation="location-list" aria-expanded="false" aria-hidden="true" class="css-43f66w"></ol><div data-automation="cc-indicative-availability" class="css-1330ege"><span>Indicative availability as of 11/11/2011 22:22</span></div></div></div></div></div>''')
    DOM3 = parser3.dom
    
    DOM1.mark_uncommon(DOM2)
    
    print(DOM1.attr_ignore_all)
    print(DOM1.attr_ignore_list)
    print(DOM1.content_ignore_all)
    print(DOM1.content_ignore_list)
    
    print(DOM1 == DOM3)
    
    
    