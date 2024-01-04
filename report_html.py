
from json.encoder import (JSONEncoder, encode_basestring_ascii, INFINITY, encode_basestring)
import json
from html import escape


# Mostly taken from json encoder: https://github.com/python/cpython/blob/main/Lib/json/encoder.py
class JSONHTMLEncoder(JSONEncoder):
    def __init__(self, flagged_fields=[], *args, **kwargs):
        self.flagged_fields = flagged_fields
        super().__init__(*args, **kwargs)
    
    def iterencode(self, o, _one_shot=False):
        """Encode the given object and yield each string
        representation as available.

        For example::

            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)

        """
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring

        def floatstr(o, allow_nan=self.allow_nan,
                _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text


        # if (_one_shot and c_make_encoder is not None
        #         and self.indent is None):
        #     _iterencode = c_make_encoder(
        #         markers, self.default, _encoder, self.indent,
        #         self.key_separator, self.item_separator, self.sort_keys,
        #         self.skipkeys, self.allow_nan)
        # else:
        _iterencode = _make_iterencode(
                markers, self.default, _encoder, self.indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot, flagged_fields=self.flagged_fields)
        return _iterencode(o, 0)


def _make_iterencode(markers, _default, _encoder, _indent, _floatstr,
        _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot,
        ## HACK: hand-optimized bytecode; turn globals into locals
        ValueError=ValueError,
        dict=dict,
        float=float,
        id=id,
        int=int,
        isinstance=isinstance,
        list=list,
        str=str,
        tuple=tuple,
        _intstr=int.__repr__,
        flagged_fields=[],
    ):

    if _indent is not None and not isinstance(_indent, str):
        _indent = ' ' * _indent

    def _iterencode_list(lst, _current_indent_level, current_path=[]):
        if not lst:
            yield '[]'
            return
        if markers is not None:
            markerid = id(lst)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = lst
        buf = '['
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '<br \>' + _indent * _current_indent_level
            separator = _item_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        first = True
        for index, value in enumerate(lst):
            if first:
                first = False
            else:
                buf = separator
            if isinstance(value, str):
                if str(current_path + [index]) in flagged_fields:
                    yield buf + "<span class='flagged'>" + escape(_encoder(value)) + "</span>"
                else:
                    yield buf + escape(_encoder(value))
            elif value is None:
                if str(current_path + [index]) in flagged_fields:
                    yield buf + "<span class='flagged'>'null'</span>"
                else:
                    yield buf + 'null'
            elif value is True:
                if str(current_path + [index]) in flagged_fields:
                    yield buf + "<span class='flagged'>'true'</span>"
                else:
                    yield buf + 'true'
            elif value is False:
                if str(current_path + [index]) in flagged_fields:
                    yield buf + "<span class='flagged'>'false'</span>"
                else:
                    yield buf + 'false'
            elif isinstance(value, int):
                # Subclasses of int/float may override __repr__, but we still
                # want to encode them as integers/floats in JSON. One example
                # within the standard library is IntEnum.
                if str(current_path + [index]) in flagged_fields:
                    yield buf + "<span class='flagged'>" + _intstr(value) + "</span>"
                else:
                    yield buf + _intstr(value)
            elif isinstance(value, float):
                # see comment above for int
                if str(current_path + [index]) in flagged_fields:
                    yield buf + "<span class='flagged'>" + _floatstr(value) + "</span>"
                else:
                    yield buf + _floatstr(value)
            else:
                yield buf
                if isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level, current_path=current_path + [index])
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level, current_path=current_path + [index])
                else:
                    chunks = _iterencode(value, _current_indent_level, current_path=current_path + [index])
                yield from chunks
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '<br \>' + _indent * _current_indent_level
        yield ']'
        if markers is not None:
            del markers[markerid]

    def _iterencode_dict(dct, _current_indent_level, current_path=[]):
        if not dct:
            yield '{}'
            return
        if markers is not None:
            markerid = id(dct)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = dct
        yield '{'
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '<br \>' + _indent * _current_indent_level
            item_separator = _item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            item_separator = _item_separator
        first = True
        if _sort_keys:
            items = sorted(dct.items())
        else:
            items = dct.items()
        for key, value in items:
            path_string = str(current_path + [key])
            # print(path_string)
            k = key
            if isinstance(key, str):
                pass
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            elif isinstance(key, float):
                # see comment for int/float in _make_iterencode
                key = _floatstr(key)
            elif key is True:
                key = 'true'
            elif key is False:
                key = 'false'
            elif key is None:
                key = 'null'
            elif isinstance(key, int):
                # see comment for int/float in _make_iterencode
                key = _intstr(key)
            elif _skipkeys:
                continue
            else:
                raise TypeError(f'keys must be str, int, float, bool or None, '
                                f'not {key.__class__.__name__}')
            if first:
                first = False
            else:
                yield item_separator
            if path_string in flagged_fields:
                yield "<span class='flagged'>" + escape(_encoder(key))
            else:
                yield escape(_encoder(key))
            yield _key_separator
            if isinstance(value, str):
                yield escape(_encoder(value))
            elif value is None:
                yield 'null'
            elif value is True:
                yield 'true'
            elif value is False:
                yield 'false'
            elif isinstance(value, int):
                # see comment for int/float in _make_iterencode
                yield _intstr(value)
            elif isinstance(value, float):
                # see comment for int/float in _make_iterencode
                yield _floatstr(value)
            else:
                if isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level, current_path=current_path + [k])
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level, current_path=current_path + [k])
                else:
                    chunks = _iterencode(value, _current_indent_level, current_path=current_path + [k])
                yield from chunks
            if path_string in flagged_fields:
                yield "</span>"
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '<br \>' + _indent * _current_indent_level
        yield '}'
        if markers is not None:
            del markers[markerid]

    def _iterencode(o, _current_indent_level):
        if isinstance(o, str):
            yield escape(_encoder(o))
        elif o is None:
            yield 'null'
        elif o is True:
            yield 'true'
        elif o is False:
            yield 'false'
        elif isinstance(o, int):
            # see comment for int/float in _make_iterencode
            yield _intstr(o)
        elif isinstance(o, float):
            # see comment for int/float in _make_iterencode
            yield _floatstr(o)
        elif isinstance(o, (list, tuple)):
            yield from _iterencode_list(o, _current_indent_level)
        elif isinstance(o, dict):
            yield from _iterencode_dict(o, _current_indent_level)
        else:
            if markers is not None:
                markerid = id(o)
                if markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = o
            o = _default(o)
            yield from _iterencode(o, _current_indent_level)
            if markers is not None:
                del markers[markerid]
    return _iterencode


def process(target):
    f = open("tests/" + target + ".json", "r")
    j = json.loads(f.read())
    f.close()
    f = open("tests/" + target + ".csv", "r")
    flag = f.read().split("\n")
    f.close()
    output_html = json.dumps(j, cls=JSONHTMLEncoder, indent="&nbsp;"*4, flagged_fields=flag)

    f = open("tests/" + target + "_flagged.html", "w")
    f.write(f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .flagged {{ color: red; }}
            </style>
        </head>
        <body>
            {output_html}
        </body>
        </html>
        ''')
    f.close()

if __name__ == "__main__":
    process("wikipedia")
