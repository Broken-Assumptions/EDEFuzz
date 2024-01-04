import copy

def mutate(resp):
    t = copy.deepcopy(resp)
    yield from mutate_wrap(t, t)

def mutate_wrap(resp, sub_resp, path=[]):
    if isinstance(sub_resp, dict) or isinstance(sub_resp, list):
        if isinstance(sub_resp, dict):
            iter = list(sub_resp.keys())
        else:
            iter = list(range(len(sub_resp)))
        
        for key in iter:
            path.append(key)
            if isinstance(sub_resp[key], dict) or isinstance(sub_resp[key], list):
                yield from mutate_wrap(resp, sub_resp[key], path)
                path.pop()
                continue
            temp = sub_resp[key]
            del sub_resp[key]
            yield copy.deepcopy(resp), copy.deepcopy(path)
            if isinstance(sub_resp, dict):
                sub_resp[path.pop()] = temp
            else:
                sub_resp.insert(path.pop(), temp)

def leaf(object, path=[]):
# ruterns a collection (generator) of path to each leaf node
    if isinstance(object, dict) or isinstance(object, list):
        if isinstance(object, dict):
            iter = list(object.keys())
        else:
            iter = list(range(len(object)))
        
        for key in iter:
            path.append(key)
            yield from leaf(object[key], path)
            path.pop()
    else:
        yield copy.deepcopy(path)

def mutate_sort(item):
    t = copy.deepcopy(item)
    return mutate_sort_warp(t)

def mutate_sort_warp(item):
    if isinstance(item, dict):
        t = {}
        for i in sorted(item.keys()):
            t[i] = mutate_sort(item[i])
    elif isinstance(item, list):
        t = []
        for i in item:
            t.append(mutate_sort(i))
    else:
        return item
    return t

if __name__ == "__main__":
    j = {"a": 5, "b": {"c": 6, "d": {"e": {"f": 1}, "g": 7, "h": 8}, "i": [2, 3]}, "j": 9}
    k = {'id': 123456, 'name': 'Hello World', 'firstname': 'Hello', 'surname': 'World', 'age': 10, 'role': 1, 'image': '/image/test.jpg'}
    l = [{"id":"24869","name":"Samuel Jones","created_at":"2019-06-07T20:52:48+10:00","sortable_name":"Jones, Samuel","short_name":"Samuel Jones","sections":"Evaluating the User Experience, Fieldwork for Design, Internship, Farrukh, Knowledge Technologies, Fieldwork for Design, Designing Novel Interactions, Year 2, Class of 2018, EligibleStudents, COM_COM_000248_SWEN90016_2020_SM2, Local Presentations, COM_COM_000189_COMP90043_2020_SM2, COM_COM_000248_COMP90043_2020_SM2, Social Computing, Workshop 1 (19), Lecture 2 (1), COM_COM_000189_SWEN90016_2020_SM2, HCI Project, COM_COM_000189_COMP90082_2020_SM2, Workshop 1 (2), AI Planning for Autonomy, Workshop 1 (17), Lecture 2 (1), MC-IT, Natural Language Processing, Lecture 1 (1), Declarative Programming, Lecture 1 (1), Workshop 1 (1), COM_COM_000248_COMP90082_2020_SM2, COM_COM_000248_COMP90042_2020_SM1, Lecture 1 (1), COM_COM_000500_COMP90082_2020_SM2, Workshop 1 (13), Lecture 1 (1), Software Processes and Management, Software Project, Lecture 2 (1), Lecture 2 (1), Workshop 1 (9), Cryptography and Security, Lecture 1 (1), Community: Technology Innovation 2020 S2, Statistical Machine Learning, COM_COM_000248_COMP90048_2020_SM1","group_submissions":[10406816],"is_inactive":False},{"id":"16176","name":"Karen Qu","created_at":"2019-06-07T18:47:22+10:00","sortable_name":"Qu, Karen","short_name":"Karen Qu","sections":"Distributed Systems, Software Processes and Management, Lecture 2 (1), Declarative Programming, Knowledge Technologies, Mobile Computing Systems Programming, Computing Project, COM_COM_000189_COMP90043_2020_SM2, EligibleStudents, COM_COM_000354_GEOM90008_2020_SM1, Year 2, Lecture 2 (1), Practical 1 (4), Workshop 1 (19), AI Planning for Autonomy, MC-IT, COM_COM_000189_GEOM90008_2020_SM1, Lecture 1 (1), Week 5, Foundations of Spatial Information, Cryptography and Security, Natural Language Processing, COM_COM_000354_GEOM90007_2020_SM2, Lecture 1 (1), Information Visualization, Lecture 1 (1), Workshop 1 (1), Cryptography and Security, Lecture 1 (1), COM_COM_000248_COMP90050_2020_SM1, COM_COM_000248_COMP90043_2020_SM2, Practical 1 (3), Advanced Database Systems, Lecture 1 (1), Lecture 2 (1), Workshop 1 (5), Class of 2018, COM_COM_000248_COMP90042_2020_SM1","group_submissions":[10406803],"is_inactive":False}]
    
    import json
    
    cw = json.load(open("tests/instagram.json",encoding="utf8"))
    
    for i in leaf(j):
        print(i)
    print(len(list(mutate(cw))))
