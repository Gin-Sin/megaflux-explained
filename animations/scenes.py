"""Original schematic animations for MegaFlux, explained.

Based on arXiv:2610.00671v1 §§2–3. These are explanatory diagrams,
not measured GPU traces. Render with scripts/render.py.
"""
from manim import *

BG = "#101D2D"
INK = "#F4F0E6"
MUTED = "#A9B8C8"
TEAL = "#65D6BC"
AMBER = "#FFC078"
VIOLET = "#B6A3F5"
BLUE = "#82B5EB"


def label(text, size=24, color=INK, **kwargs):
    return Text(text, font="DejaVu Sans", font_size=size, color=color, **kwargs)


def pill(text, width, color, center, height=0.6, size=21):
    box = RoundedRectangle(width=width, height=height, corner_radius=0.08,
                           stroke_color=color, fill_color=color, fill_opacity=0.17)
    txt = label(text, size, color).move_to(box)
    if txt.width > width - 0.12:
        txt.scale_to_fit_width(width - 0.12)
    return VGroup(box, txt).move_to(center)


class Base(Scene):
    def setup(self):
        self.camera.background_color = BG

    def heading(self, number, title, subtitle):
        tag = label(f"MEGAFLUX / {number}", 17, TEAL).to_edge(UP, buff=0.33).to_edge(LEFT, buff=0.65)
        title_obj = Text(title, font="CMU Serif", font_size=40, color=INK).next_to(tag, DOWN, aligned_edge=LEFT, buff=0.22)
        sub = label(subtitle, 19, MUTED).next_to(title_obj, DOWN, aligned_edge=LEFT, buff=0.2)
        self.add(tag, title_obj, sub)

    def foot(self, text):
        return label(text, 18, MUTED).to_edge(DOWN, buff=0.35)


class RoutingSkew(Base):
    def construct(self):
        self.heading("01", "The busiest GPU sets the pace", "Four GPUs. Same routed work. Different execution locations.")
        colors = [AMBER, TEAL, BLUE, VIOLET]
        ys = [1.25, 0.1, -1.05, -2.2]
        blocks, counts = [], []
        for r, y in enumerate(ys):
            self.add(label(f"GPU {r}", 24).move_to([-5.55, y + 0.05, 0]))
            self.add(label(f"owns E{r}", 16, MUTED).move_to([-5.55, y - 0.31, 0]))
            self.add(Line([-4.4, y - 0.42, 0], [5.85, y - 0.42, 0], color="#314153"))
            row = VGroup()
            for j in range(12 if r == 0 else 4):
                b = RoundedRectangle(width=0.5, height=0.5, corner_radius=0.06,
                                     stroke_width=0, fill_color=colors[r], fill_opacity=1)
                b.move_to([-3.9 + j * 0.59, y, 0])
                row.add(b)
            blocks.append(row)
            n = label("12 blocks" if r == 0 else "4 blocks", 23, colors[r]).move_to([4.8, y, 0])
            counts.append(n)
        status = self.foot("24 blocks total  |  Slowest GPU: 12 blocks")
        self.play(*[FadeIn(row, shift=RIGHT * .2) for row in blocks], *[FadeIn(n) for n in counts], FadeIn(status), run_time=1.4)
        self.wait(2)
        replica_labels = VGroup(*[label("+ E0 replica", 17, AMBER).move_to([4.8, ys[r] - .31, 0]) for r in [1, 2, 3]])
        reminder = label("Copy E0 weights to each receiver", 20, AMBER).move_to([0, -3.0, 0])
        self.play(FadeIn(replica_labels), FadeIn(reminder), run_time=.8)
        self.wait(1.5)
        moves = []
        for r in [1, 2, 3]:
            for j in range(2):
                b = blocks[0][6 + (r - 1) * 2 + j]
                moves.append(b.animate.move_to([-3.9 + (4+j) * .59, ys[r], 0]))
        self.play(*moves, run_time=2.2)
        new_counts = [label("6 blocks", 23, TEAL).move_to(n) for n in counts]
        self.play(*[Transform(a, b) for a, b in zip(counts, new_counts)],
                  Transform(status, self.foot("24 blocks total  |  Slowest GPU: 6 blocks")),
                  Transform(reminder, label("Compute-only illustration; replication has a cost", 19, MUTED).move_to(reminder)), run_time=1)
        self.wait(3.2)


class ForwardPipeline(Base):
    def construct(self):
        self.heading("02", "Start when this phase is ready", "FC1 needs W1 + input. FC2 needs W2 + the FC1 activation.")
        self.add(label("Separate stages", 22, MUTED).move_to([-4.9, 1.5, 0]))
        # Bar widths are deliberately schematic, not benchmark timings.
        top = VGroup(pill("W1 transfer", 2.2, AMBER, [-3.0, .75, 0]),
                     pill("W2 transfer", 2.2, AMBER, [-.7, .75, 0]),
                     pill("FC1", 2.2, TEAL, [1.6, .75, 0]),
                     pill("FC2", 2.2, BLUE, [3.9, .75, 0]))
        self.play(LaggedStart(*[FadeIn(x) for x in top], lag_ratio=.25), run_time=2)
        self.wait(1)
        self.add(label("Pipelined", 22, TEAL).move_to([-5.55, -.35, 0]))
        self.add(label("transfer", 18, MUTED).move_to([-5.45, -1.05, 0]))
        self.add(label("compute", 18, MUTED).move_to([-5.45, -2.0, 0]))
        w1 = pill("W1 transfer", 2.2, AMBER, [-3.0, -1.05, 0])
        w2 = pill("W2 transfer", 2.2, AMBER, [-.7, -1.05, 0])
        fc1 = pill("FC1", 2.2, TEAL, [-.7, -2, 0])
        fc2 = pill("FC2", 2.2, BLUE, [1.6, -2, 0])
        self.play(FadeIn(w1), run_time=1)
        ready1 = DashedLine([-1.85, -.55, 0], [-1.85, -2.45, 0], color=TEAL)
        note = MathTex(r"W_1", r"+", r"X", r"\ \mathrm{ready}\ \Rightarrow\ \mathrm{FC1}", font_size=26, color=TEAL).move_to([1.5, -.4, 0])
        note[0].set_color(AMBER)
        self.play(Create(ready1), FadeIn(note), run_time=.6)
        self.play(FadeIn(w2), FadeIn(fc1), run_time=1.3)
        self.wait(2)
        ready2 = DashedLine([.45, -.6, 0], [.45, -2.45, 0], color=BLUE)
        self.play(Create(ready2), FadeIn(fc2),
                  Transform(note, MathTex(r"W_2", r"+", r"A", r"\ \mathrm{ready}\ \Rightarrow\ \mathrm{FC2}", font_size=26, color=BLUE).move_to(note).set_color_by_tex("W_2", AMBER)), run_time=1)
        self.add(self.foot("Schematic time →  |  FC1 overlaps W2 transfer  |  No full-replica wait"))
        self.wait(3.3)


class BackwardReduction(Base):
    def construct(self):
        self.heading("03", "Advance the last missing partial", "A gradient tile can reduce only when every participant is ready.")
        names = ["Owner", "Replica A", "Replica B"]
        ys = [1.45, .35, -.75]
        bars = []
        for i, (name, y) in enumerate(zip(names, ys)):
            self.add(label(name, 21).move_to([-5.45, y, 0]))
            width = 2 + i * .85
            bar = pill("produce tile 0", width, VIOLET, [-3.95 + width / 2, y, 0], size=18)
            bars.append(bar)
        self.play(*[FadeIn(b) for b in bars], run_time=1.2)
        dots = [Dot([bars[i].get_right()[0] + .18, y, 0], color=TEAL, radius=.08) for i,y in enumerate(ys)]
        status = label("Waiting for replica B", 22, AMBER).move_to([.7, -2.7, 0])
        self.play(FadeIn(dots[0]), FadeIn(dots[1]), FadeIn(status), run_time=.9)
        self.wait(2.2)
        self.play(FadeIn(dots[2]), Transform(status, label("All tile 0 partials ready", 22, TEAL).move_to(status)), run_time=.9)
        reduction = pill("reduce tile 0", 2.5, TEAL, [1.6, -1.9, 0], size=21)
        self.add(label("At owner", 18, MUTED).move_to([-5.45, -1.9, 0]))
        self.play(FadeIn(reduction), run_time=.6)
        later = VGroup(*[pill("later tiles", 2.5, BLUE, [1.6, y, 0], size=20) for y in ys])
        self.play(FadeIn(later), run_time=.7)
        # Fixed-order contributions illustrate accumulation after all partials exist.
        for i in range(3):
            contrib = Dot(dots[i].get_center(), color=VIOLET, radius=.10)
            self.add(contrib)
            self.play(contrib.animate.move_to(reduction.get_center()), run_time=.5)
            self.remove(contrib)
        self.play(Transform(status, label("Prioritize this expert on every participant", 22, TEAL).move_to(status)), run_time=.7)
        self.add(self.foot("Schematic WGrad timeline  |  FP32 reduction overlaps later computation"))
        self.wait(3)
