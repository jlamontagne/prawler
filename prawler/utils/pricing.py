import re
from collections import namedtuple
from prawler.utils.misc import decompose_all, text
from itertools import chain, groupby, izip_longest

Quantity = namedtuple('Quantity', ['quantity', 'index', 'row'])

# 250, 2,500, 250+, 250-499, etc
quantity_re = re.compile('^(\d+(?:,\s*\d+)?)\s*-?\s*[,\s\d]*\+?$')
price_re = re.compile('^\$?(\d*\.\d\d)\d*(?:\s|$)')
discount_re = re.compile(r"""(?:^|\s) \(? \s*
                             (?!CAD|cad|USA|usa|USD|usd) (
                               (?:[1-9P-VA-GX]*[P-VA-GX]+) |
                               (?:[1-9p-va-gx]*[p-va-gx]+)
                             ) \s* \)? (?:\s|$)""", re.X)

def price_str(string):
    matches = price_re.search(text(string))
    if matches:
        return matches.group(1).encode('ascii', errors='ignore')

def quant_str(string):
    matches = quantity_re.search(text(string))
    if matches:
        return re.sub('[,\+]', '', matches.group(1).encode('ascii', errors='ignore'))

def row_price(tag):
    """Return True if tag is a price cell in a price row."""
    if not price_str(tag) or (tag.name != 'td' and tag.name != 'th'):
        return False

    # A price cell must have at least one price cell neighbour
    for sibling in chain(tag.previous_siblings, tag.next_siblings):
        if price_str(sibling):
            return True

def column_price(tag):
    """Return True if tag is a price cell in a price column."""
    if not price_str(tag) or (tag.name != 'td' and tag.name != 'th'):
        return False

    # A price cell must have at least one price cell neighbour
    uncles = chain(tag.parent.previous_siblings, tag.parent.next_siblings)
    cousins = [tag for tag in chain.from_iterable(uncles) if price_str(tag)]
    return cousins

def get_discount_code(tags, depth=3):
    """Find a discount code by expanding the search outwards."""
    for tag in tags:
        matches = discount_re.search(text(tag))

        if matches:
            return matches.group(1).encode('ascii', errors='ignore')
        elif tag.parent and depth:
            code = get_discount_code([tag.parent], depth - 1)
            if code:
                return code.encode('ascii', errors='ignore')

def extract_price_info(soup):
    # Find price tables by searching upwards from price cells
    price_cells = soup.find_all(row_price)
    transpose = False

    if not price_cells:
        price_cells = soup.find_all(column_price)
        transpose = True

    dom_tables = [cell.find_parent('table') for cell in price_cells]

    # Remove duplicates while preserving order
    dom_tables = [table for table, _ in groupby(dom_tables)]

    # Convert dom tables to matrices and transpose if necessary
    matrices = [[[text(c) for c in r] for r in t('tr')] for t in dom_tables]

    if transpose:
        matrices = [list(izip_longest(*m)) for m in matrices]

    discount_code = get_discount_code(dom_tables)
    decompose_all(dom_tables)
    return (matrices, discount_code)

def indices(x):
    return range(0, len(x))

def get_quantity_info(m):
    is_q = lambda j, i: quant_str(m[j][i])
    info = lambda j, i: Quantity(quant_str(m[j][i]), index=i, row=j)

    # Find quantities and quantity indexes. Use the longest matching row.
    q = [[info(j, i) for i in indices(m[j]) if is_q(j, i)] for j in indices(m)]
    q = max(q, key=len)

    if q:
        return (q, q[0].row)
    else:
        return (None, None)

def get_prices(soup):
    pricing = []
    matrices, discount_code = extract_price_info(soup)

    """
    +-------------------------------------------------+
    | Quantity |   100 |   250 |   500 |  1000 | None |
    |----------+-------+-------+-------+-------+------|
    |  XYZ-123 | $4.00 | $3.85 | $3.25 | $2.50 | None |
    |----------+-------+-------+-------+-------+------|
    |  ABC-456 | $5.00 | $4.50 | $2.55 | $1.00 | (5C) |
    +-------------------------------------------------+
    """
    for m in matrices:
        quants, q_row = get_quantity_info(m)

        if not quants:
            continue

        for row in m[q_row + 1:]:
            first_price_i = quants[0].index
            last_price_i = quants[-1].index

            if last_price_i >= len(row):
                # Insufficient price columns in row
                continue

            name = ''
            names = [cell for cell in row[:first_price_i] if cell]

            if names:
                name = names[0]

            if names[1:]:
                name += ' ({})'.format(', '.join(names[1:]))

            pr = {'name': name, 'columns': []}

            for i in indices(quants):
                quantity = quants[i].quantity

                j = quants[i].index
                price = price_str(row[j])

                if price:
                    pr['columns'].append({'quantity': quantity, 'price': price})

            if pr['columns']:
                pricing.append(pr)

    return (pricing, discount_code)
