from micropython import const
from trezor import loop, ui, res
from .swipe import Swipe, SWIPE_UP, SWIPE_DOWN, SWIPE_VERTICAL


async def change_page(page, page_count):
    while True:
        if page == 0:
            d = SWIPE_UP
        elif page == page_count - 1:
            d = SWIPE_DOWN
        else:
            d = SWIPE_VERTICAL
        s = await Swipe(directions=d)
        if s == SWIPE_UP:
            return page + 1  # scroll down
        elif s == SWIPE_DOWN:
            return page - 1  # scroll up


async def paginate(render_page, page_count, page=0, *args):
    while True:
        changer = change_page(page, page_count)
        renderer = render_page(page, page_count, *args)
        waiter = loop.wait(changer, renderer)
        result = await waiter
        if changer in waiter.finished:
            page = result
        else:
            return result


async def animate_swipe():
    time_delay = const(40000)
    draw_delay = const(200000)

    sleep = loop.sleep(time_delay)
    for t in ui.pulse(draw_delay):
        fg = ui.blend(ui.GREY, ui.DARK_GREY, t)
        ui.display.text_center(110, 210, 'Swipe', ui.NORMAL, fg, ui.BG)
        await sleep


def render_scrollbar(page, page_count):
    bbox = const(220)
    size = const(10)

    padding = 15
    if page_count * padding > bbox:
        padding = bbox // page_count

    x = const(225)
    y = (bbox // 2) - (page_count // 2) * padding

    for i in range(0, page_count):
        if i != page:
            ui.display.bar_radius(x, y + i * padding, size,
                                  size, ui.DARK_GREY, ui.BG, 4)
    ui.display.bar_radius(x, y + page * padding, size,
                          size, ui.FG, ui.BG, 4)

    if page != 0:
        ui.display.icon(x-1, y - 20, res.load(ui.ICON_UP), ui.FG, ui.BG)

    if page + 1 != page_count:
        ui.display.icon(x-1, y + (page_count * padding) + 10, res.load(ui.ICON_DOWN), ui.FG, ui.BG)


class Scrollpage(ui.Widget):

    def __init__(self, content, page, page_count):
        self.content = content
        self.page = page
        self.page_count = page_count

    def render(self):
        self.content.render()
        render_scrollbar(self.page, self.page_count)

    async def __iter__(self):
        return await loop.wait(super().__iter__(), self.content)
