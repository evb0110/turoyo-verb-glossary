"""Split boxes into source-order examples, without changing the source text."""

import re

from .docx import Text, join

NUMBER = re.compile(r"(?<![\w/:.])(\d{1,2})\)(?=\s|[^\W\d_]|[‘ʻ\"(\[]|$)\s*")
PREFIX = r"(?:prs|PrS|JL|Jl|LB|MM|LuF|EL|RT|DD|QM|HD|Lehrbuch|jastr|lj)\.?"
LOCATION = r"(?:[IVX]+\.)?\d+(?:[./]\d+)*(?:\s*[-–,]\s*\d+(?:[./]\d+)*)*"
REF = re.compile(
    rf"(?P<prefixed>{PREFIX}\s*{LOCATION})"
    r"|(?P<tag>\[(?:MT|LTN|ML|FKD|SL|ST)\]|(?-i:ST|IT|BS|SB|RBP)\b)"
    r"|(?P<source>(?:[\w.-]+_[\w.-]+(?:[ .\w-]*?)[;,]\s*\d{1,2}:\d{2}"
    r"|Xori[- ]Caziz[^;\n]*|Malfono_Ishaq,\d+[’']?|NE_Ezo_Koviye\b"
    r"|Maḥkay Ḥḏo Ḥreto \d+ \d+:\d+|Shabo\b|Jan\(\)))"
    r"|(?P<corpus>(?:[A-Z][\w.-]*_[\w.-]+|NE|SZ|Jan|Hanna Dewo)\s*\d*[;/]\d+)"
    r"|(?P<context>\([^()\n]*(?:\d+[:.]\s*\d+|_\w+|\b(?:HD|NE|FG|Xori[- ]Caziz)\b)[^()\n]*\))"
    r"|(?P<text>\d{1,3}/\d{1,4}(?:\s*[-–,]\s*\d+)*)"
    r"|(?P<page>\d{1,4}(?:\s*[-–]\s*\d+)?)"
    r"|(?P<pc>(?:\([^()\n]*\bp\.?c\.?[^()\n]*\)?|p\.?c\.?\s+[\wʕʔḤİŠš -]+|[\wʕʔḤİŠš. -]+\bp\.?c\.?)"
    r"(?:\s+(?:[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4}))?)",
    re.IGNORECASE,
)
OPEN = "ʻ‘ʽ„“\"'"
CLOSE = "ʼ’ʾ”\"'"
PAIRS = {"ʻ": "ʼ", "‘": "’", "ʽ": "ʼ", "„": "“", "“": "”", '"': '"', "'": "'"}


def closing_quote(text, begin, italic=()):
    stack = [PAIRS[text[begin]]]
    for i in range(begin + 1, len(text)):
        char = text[i]
        # Plural possessives inside English glosses are not closing marks.
        following = re.match(r"\s+([a-z])", text[i + 1:])
        if char in "’ʼ'" and text[i - 1:i].lower() == "s" and following:
            after = i + 1 + following.start(1)
            if ((italic and not italic[after] or re.match(r"(?:and|or)\b", text[after:]))
                    and not re.match(r"(?:see|cf|note)\b", text[after:], re.I)
                    and any(c in text[i + 1:] for c in "’ʼ'")):
                continue
        if char in CLOSE + "“" and (i + 1 == len(text) or not text[i + 1].isalpha() or text[i + 1] in CLOSE):
            same_family = (char in "ʼ’ʾ'" and stack[-1] in "ʼ’ʾ'") or (char in '”"' and stack[-1] in '”"')
            if char == stack[-1] or same_family:
                stack.pop()
                if not stack:
                    return i
                continue
        if char in PAIRS and text[i - 1] in " \t\n(:" + OPEN and i + 1 < len(text) and not text[i + 1].isspace():
            stack.append(PAIRS[char])
    return None


def refs_at_start(text, start=0):
    """Consume only citation tokens, never scan arbitrary example prose for digits."""
    result, pos = [], start
    while True:
        delimiter = re.match(r"[\s;,]*", text[pos:])
        begin = pos + delimiter.end()
        if "\n" in delimiter[0]:
            # A new example can start with its source label or verse number.
            # Consume a citation paragraph only when the whole line is a cite.
            line = text[begin:].split("\n", 1)[0]
            found, tail = refs_at_start(line)
            if not found or line[tail:].strip():
                return result, begin
        if NUMBER.match(text, begin):
            return result, begin
        match = REF.match(text, begin)
        if not match:
            return result, begin
        # A bare page must end at punctuation/whitespace, not inside a word/date.
        if match.end() < len(text) and text[match.end()] not in " \t\n;,.)[":
            return result, begin
        if match.lastgroup == "page" and re.match(r"\.(?:\d|\s+\S)", text[match.end():]):
            return result, begin
        raw = match[0]
        kind, text_id, verse = "other", None, None
        if match.lastgroup == "prefixed":
            prefix = re.match(r"[A-Za-z]+", raw)[0].lower()
            kind = {"prs": "prs", "jl": "jl", "lb": "lb", "mm": "mm", "luf": "luf"}.get(prefix, "other")
        elif match.lastgroup == "text":
            number, v = re.match(r"(\d+)/(\d+)", raw).groups()
            kind, text_id, verse = "text", f"R{int(number):03d}", int(v)
        elif match.lastgroup == "page":
            kind = "grammar-page"
        result.append({"raw": raw, "kind": kind, "textId": text_id, "verse": verse})
        pos = match.end()


# Only explicit English syntax is a fallback when source formatting is absent
# or inverted. In particular, Turoyo's article "I" alone is not an English cue.
ENGLISH = re.compile(
    r"(?:(?:I|we|you|he|she|they|it)\s+(?:am|are|is|was|were|will|would|shall|should|can|could|must|have|has|had|do|does|did|went|got|spent|rely|support|claspes|reached|gave|picked|plunged|changed|threw|swears|said|put|promised|trampled)\b"
    r"|(?:are|is|did|does|do|can|could|will|would)\s+(?:they|he|she|it|there|you|we|the)\b"
    r"|(?:the|this|that|those|all|nine|people|smoking|leaves|grapes)\s+"
    r"|(?:now|then|once|well|songs|oh|so|today|till)\b[,!?.]?\s+|(?:yes|no)[,!]\s+"
    r"|(?:and|but|because|in)\s+(?:the|this|that|he|she|they|we|all|Bakkoye)\b|as\s+long\b"
    r"|does\s+not\b|tea\s+dissolved\b|are\s+the\b|my\s+life\b|because\s+of\b"
    r"|(?:my|your|his|her|our|their)\s+\w+\s+(?:was|is|were|are|has|have)\b"
    r"|damned\s+by\b"
    r"|(?-i:[A-Z][a-z]+)(?:\s+and\s+(?-i:[A-Z][a-z]+))?\s+(?:did|does|was|were|has|have|is|are|will|induced|moved|made|remained|bring|becomes|drafts|craved|stole)\b)",
    re.I,
)


def translation_span(value: Text, start=0):
    """Find the earliest gloss, using its letters rather than its quote's font.

    A citation after a closed quote is also decisive when the entire translation
    was accidentally italicised. Unquoted English is accepted only with explicit
    syntax; other unformatted material remains verbatim for proofreading.
    """
    text = value.text
    initial = start + len(text[start:]) - len(text[start:].lstrip())
    candidates = [i for i in range(start, len(text))
                  if text[i] in OPEN and i > start and text[start:i].strip()
                  and (text[i - 1].isspace() or text[i - 1] in ":;,.!?" + OPEN)]
    if ((ENGLISH.match(text, initial) and not any(any(value.italic[initial:i]) for i in candidates))
            or re.match(r"(?:Dear\b|\S+ knows of no\b)", text[initial:])):
        return None
    quoted, fallback = None, None
    for begin in candidates:
        prefix = NUMBER.sub("", text[start:begin], count=1).strip()
        if not any(c.isalpha() for c in prefix):
            continue
        if (not any(value.italic[start:begin])
                and re.fullmatch(r"[\w\s]{1,30}:\s*", text[start:begin])):
            continue
        end = closing_quote(text, begin, value.italic)
        if end is None:
            end = begin + 1
            while end < len(text) and text[end] != "\n" and (not value.italic or not value.italic[end]):
                end += 1
            if end > begin + 1:
                quoted = (begin, begin + 1, end, end)
                break
            continue
        span = (begin, begin + 1, end, end + 1)
        letters = [j for j in range(begin + 1, end) if text[j].isalpha()]
        roman = not value.italic or (letters and sum(not value.italic[j] for j in letters) > len(letters) / 2)
        cited = bool(refs_at_start(text, end + 1)[0])
        # Unformatted direct speech is still Turoyo, even when Word marks it
        # roman. A later English paragraph may supply the actual translation.
        if (not any(value.italic[start:begin]) and not cited
                and (re.search(r"[əәǝʕʔḏḥṭṣšġǧṯḷ]|\w+-(?:yo|no)\b", text[begin + 1:end])
                     or re.search(r"(?:komar|məlle|məḷḷe|ǝmmo|əmmo)\s*[,.:]?\s*$", prefix))
                and not ENGLISH.match(text[begin + 1:end])):
            continue
        if roman or cited:
            quoted = span
            break
        if fallback is None:
            fallback = span

    limit = quoted[0] if quoted else len(text)
    has_turoyo, roman_until, previous = False, start, start
    for match in re.finditer(r"[^\W\d_]+", text[start:limit]):
        i = start + match.start()
        if "\n" in text[previous:i]:
            has_turoyo = False
        previous = i
        if value.italic and value.italic[i]:
            has_turoyo = True
        if not text[start:i].strip():
            continue
        if i and not (text[i - 1].isspace() or text[i - 1] in "=([–.?!:;"):
            continue
        english = ENGLISH.match(text, i)
        # An italic -> roman boundary is stronger than language heuristics.
        formatted = has_turoyo and value.italic and not value.italic[i] and i >= roman_until
        if not english and not formatted:
            continue
        if quoted and text[start:i].count("(") > text[start:i].count(")"):
            continue
        end = i
        while end < len(text):
            if (text[end] == "\n" and not (english and end < english.end())) or (not value.italic[i] and value.italic[end] and text[end].isalpha()):
                break
            end += 1
        roman_until = end
        tail = text[i:end]
        if re.match(r"(?:Пример\b|Надо\b|Выпала\b|cf\.|see\b|Note\b|SL\b|turkish:|is preferred\b)", tail, re.I):
            continue
        refs, consumed = refs_at_start(text, i)
        if refs:
            continue
        if re.fullmatch(r"[\wʕʔḤİ. ,;-]*\bp\.?c\.?[\s).,;]*", tail, re.I):
            continue
        if sum(c.isalpha() for c in tail) < 3:
            continue
        if re.search(r"\betc[.…]", tail) and text[:i].rstrip().endswith("("):
            continue
        # References and source labels can be roman too. End the gloss before
        # its citation, keeping the citation available to the same scanner.
        for delimiter in re.finditer(r"[;\n]|\s*(?=\([^()\n]*\bp\.?c\.?)|\s+(?=" + PREFIX + r"\s*\d)", text[i:], re.I):
            if i + delimiter.start() > end:
                break
            offset = i + delimiter.end()
            found, _ = refs_at_start(text, offset)
            if found:
                end = i + delimiter.start()
                break
        remark = re.search(r"\s*(?:=|We shall have to doublecheck\b|:\s*[^:\n]{1,30}:\s*[“‘ʻ])", text[i:end])
        if remark:
            end = i + remark.start()
        # Parentheses are also used as translation delimiters. Do not leave
        # their opening mark in Turoyo or absorb following Turoyo into English.
        before = text[:i].rstrip()
        if before.endswith("("):
            close, depth = i, 1
            while close < len(text) and depth:
                depth += (text[close] == "(") - (text[close] == ")")
                close += 1
            if not depth:
                return len(before) - 1, i, min(end, close - 1), close
        return i, i, end, end
    return quoted or fallback


def split_examples(value: Text, initial_sense=None):
    """Return raw-preserving (sense, rich text) pairs; inherit a numbered group."""
    text = value.text
    # Paragraphs are reliable boundaries, except a separately typed translation
    # or citation paragraph, which belongs to the preceding example.
    boundaries = {0, len(text)}
    for match in re.finditer(r"\n+", text):
        after = text[match.end():]
        if after.strip() and not after.lstrip().startswith(tuple(OPEN)):
            refs, end = refs_at_start(after)
            if (not refs or after[end:].strip()) and not ENGLISH.match(after.lstrip()):
                boundaries.add(match.end())
    # Parenthesised citations contain timestamps such as '(209 FG 15: 04)'.
    # Their closing minutes are not numbered senses, nor are numbers in glosses.
    protected = []
    # A translation + citations ends an example even within one paragraph.
    pos = 0
    while pos < len(text):
        span = translation_span(value, pos)
        if span is None:
            break
        _, _, _, end = span
        protected.append((span[0], end))
        boundaries = {b for b in boundaries if b == 0 or b == len(text)
                      or not (span[0] <= b < end or b <= span[0] and not text[b:span[0]].strip())}
        _, tail = refs_at_start(text, end)
        boundaries = {b for b in boundaries if b == 0 or b == len(text) or not end <= b < tail}
        # A passage may have several Turoyo paragraphs followed by one English
        # paragraph. Join the unfinished paragraphs, but retain boundaries after
        # a preceding translated or explicitly cited example.
        if span[0] == span[1]:
            line = text.rfind("\n", pos, span[0]) + 1
            if not text[line:span[0]].strip() or re.fullmatch(r"\d+[:.]\s*", text[line:span[0]]):
                boundaries.discard(line)
                preceding = sorted(b for b in boundaries if pos < b < line)
                for boundary in reversed(preceding):
                    previous = text[text.rfind("\n", pos, boundary - 1) + 1:boundary]
                    if re.search(r"[;)]\s*$", previous) or NUMBER.match(text, boundary):
                        break
                    boundaries.discard(boundary)
        # Closing citation parentheses and editorial '(???)' can intervene
        # before the next italic example on the same line.
        annotation_end = tail
        while True:
            annotation = re.match(r"[\s;,)]+|\([^()\n]*\)|\[[^\]\n]*\]", text[annotation_end:])
            if not annotation:
                break
            annotation_end += annotation.end()
        if annotation_end < len(text) and value.italic and value.italic[annotation_end] and text[annotation_end].isalpha():
            tail = annotation_end
        if tail < len(text) and text[tail:].strip():
            # Do not split an editorial note off as another Turoyo example.
            rest = text[tail:]
            first = rest[:120].split("\n", 1)[0]
            next_turoyo = (value.italic and value.italic[tail]) or re.search(r"[əәǝʕʔḏḥṭṣšġǧṯḷ]", first)
            if ((NUMBER.match(rest) or (rest[0].isalpha() or re.match(r"\d+\.\s+[A-Za-z]", rest)) and next_turoyo)
                    and not re.match(r"[А-Яа-яЁё]|(?:cf\.|see\b|Note\b|SL\b)", rest)):
                boundaries.add(tail)
        pos = max(end, tail, pos + 1)
    depth = 0
    markers = {m.start(): m for m in NUMBER.finditer(text)}
    for i, char in enumerate(text):
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        if i in markers and not depth and not any(a <= i < b for a, b in protected):
            boundaries.add(i)
    cuts = sorted(boundaries)
    current_sense, result, pending = initial_sense, [], None
    for begin, end in zip(cuts, cuts[1:]):
        part = value.cut(begin, end)
        if not part.text.strip():
            continue
        if pending:
            part, pending = join([pending, part], ""), None
        refs, tail = refs_at_start(part.text)
        if result and refs and not part.text[tail:].strip():
            n, previous = result[-1]
            result[-1] = n, join([previous, part], "")
            continue
        if re.fullmatch(r"\s*[a-z]\)\s*", part.text):
            pending = part
            continue
        marker = NUMBER.match(part.text.lstrip())
        if marker:
            current_sense = marker[1]
        result.append((current_sense, part))
    if pending:
        result.append((current_sense, pending))
    return result


def parse_example(value: Text, sense, identifier):
    raw = value.text.strip()
    left = len(value.text) - len(value.text.lstrip())
    value = value.cut(left, left + len(raw))
    marker = NUMBER.match(raw)
    start = marker.end() if marker else 0
    span = translation_span(value, start)
    translation, note, refs = None, None, []
    if span:
        begin, tr_start, tr_end, end = span
        turoyo = raw[start:begin].strip()
        translation = raw[tr_start:tr_end].strip() or None
        refs, tail = refs_at_start(raw, end)
        note = raw[tail:].strip() or None
    else:
        # Without a translation, only a citation-looking tail after punctuation
        # can be extracted safely. Keep everything else in the original raw.
        turoyo = raw[start:].strip()
        for match in re.finditer(r"[;\n]|\s(?=(?:prs|PrS|JL|LB|MM|LuF)\s*\d)|\s+(?=\([^()\n]*\bp\.?c\b)", raw[start:], re.I):
            offset = start + match.end()
            found, tail = refs_at_start(raw, offset)
            if found:
                turoyo = raw[start:start + match.start()].strip()
                refs, note = found, raw[tail:].strip() or None
                break
        if not refs and not any(flag and char.isalpha() for char, flag in zip(value.text, value.italic)):
            note = raw
    return {"id": identifier, "sense": sense, "turoyo": turoyo,
            "translation": translation, "refs": refs, "note": note, "raw": raw}
