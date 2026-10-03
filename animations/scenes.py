"""Dependency-driven, original Manim scenes for arXiv:2610.00671v1.

Typography is semantic: prose=Lato, code=DejaVu Sans Mono, math=MathTex.
3Blue1Brown references inform object continuity, guided attention, and pacing.
All schedules and the 2x2 gradient values are explanatory, not measurements.
"""
from pathlib import Path
import json
from manim import *
from manimpango import list_fonts

BG, INK, MUTED = "#101D2D", "#F4F0E6", "#B9C6D4"
TEAL, AMBER, VIOLET, BLUE = "#65D6BC", "#FFC078", "#B6A3F5", "#82B5EB"
PROSE_FONT, CODE_FONT, TITLE_FONT = "Lato", "DejaVu Sans Mono", "CMU Serif"
REGISTRY = []


def prose(text, size=26, color=INK, **kwargs):
    obj = Text(text, font=PROSE_FONT, font_size=size, color=color, **kwargs)
    obj.typography_role = "prose"
    REGISTRY.append({"role": "prose", "font": PROSE_FONT, "source": text})
    return obj


def code_text(text, size=24, color=INK, **kwargs):
    obj = Text(text, font=CODE_FONT, font_size=size, color=color, **kwargs)
    obj.typography_role = "code"
    REGISTRY.append({"role": "code", "font": CODE_FONT, "source": text})
    return obj


def math_tex(*tex, size=36, color=INK, **kwargs):
    obj = MathTex(*tex, font_size=size, color=color, **kwargs)
    obj.typography_role = "math"
    REGISTRY.append({"role": "math", "font": "LaTeX / Computer Modern", "source": " ".join(tex)})
    return obj


def readiness_code(weight, operand, operation, color):
    condition = f"if ready({weight}) and ready({operand}):"
    first = code_text(condition, 23)
    second = code_text(f"    run({operation})", 23, color)
    block = VGroup(first, second).arrange(DOWN, aligned_edge=LEFT, buff=.15)
    # VGroup aligns visible glyph bounds, stripping the apparent leading spaces.
    # Restore four monospace columns explicitly after alignment.
    second.shift(RIGHT * (first.width / len(condition)) * 4)
    first.set_color_by_t2c({"if": VIOLET, "and": VIOLET, weight: AMBER, operand: TEAL})
    return block


def panel(width, height, color, center, opacity=.09):
    return RoundedRectangle(width=width, height=height, corner_radius=.10,
                            stroke_color=color, stroke_width=1.8,
                            fill_color=color, fill_opacity=opacity).move_to(center)


def weight_badge(center):
    box = panel(.88, .58, AMBER, center, .18)
    return VGroup(box, math_tex("E_0", size=30, color=AMBER).move_to(box))


def track(tex, center, color, mode="math", width=2.14):
    shell = panel(width, .64, color, center, .04)
    txt = (math_tex(tex, size=32, color=color) if mode == "math"
           else code_text(tex, size=25, color=color)).move_to(shell)
    result = VGroup(shell, txt)
    result.shell, result.label = shell, txt
    result.progress = Rectangle(width=width-.06, height=.58, stroke_width=0,
                                fill_color=color, fill_opacity=.35).move_to(shell)
    return result


class Base(Scene):
    def setup(self):
        missing={PROSE_FONT,CODE_FONT,TITLE_FONT}-set(list_fonts())
        if missing:
            raise RuntimeError(f"Required fonts unavailable; refusing fallback: {sorted(missing)}")
        REGISTRY.clear()
        self.camera.background_color = BG
        self.checkpoints = []

    def heading(self, number, title, subtitle):
        tag = prose(f"MEGAFLUX / {number}", 19, TEAL).to_edge(UP, buff=.30).to_edge(LEFT, buff=.60)
        name = Text(title, font=TITLE_FONT, font_size=42, color=INK).next_to(tag, DOWN, aligned_edge=LEFT, buff=.19)
        name.typography_role = "title"
        REGISTRY.append({"role": "title", "font": TITLE_FONT, "source": title})
        sub = prose(subtitle, 24, MUTED).next_to(name, DOWN, aligned_edge=LEFT, buff=.14)
        self.add(tag, name, sub)

    def foot(self, text):
        return prose(text, 22, MUTED).to_edge(DOWN, buff=.29)

    def checkpoint(self, label):
        overflow = []
        for obj in self.get_mobject_family_members():
            if hasattr(obj, "typography_role") and obj.width > 0:
                if obj.get_left()[0] < -7.0 or obj.get_right()[0] > 7.0 or obj.get_top()[1] > 3.85 or obj.get_bottom()[1] < -3.85:
                    overflow.append({"role": obj.typography_role, "center": obj.get_center().tolist(), "width": obj.width, "height": obj.height})
        self.checkpoints.append({"name": label, "time": round(float(self.time), 2), "overflow": overflow})
        if overflow:
            raise ValueError(f"Text outside frame at {label}: {overflow}")

    def finish(self):
        self.wait(3)
        self.checkpoint("final reading hold")
        folder = Path("media/audit")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{type(self).__name__}.json").write_text(json.dumps({
            "scene": type(self).__name__, "duration": round(float(self.time), 2),
            "typography": list(REGISTRY), "checkpoints": self.checkpoints,
        }, indent=2))


class RoutingSkew(Base):
    def construct(self):
        self.heading("01", "Follow the same blocks", "Replicate the expert. Redistribute its work.")
        colors, ys = [AMBER, TEAL, BLUE, VIOLET], [1.35, .25, -.85, -1.95]
        rows, counts = [], []
        for r, y in enumerate(ys):
            gpu = VGroup(prose(f"GPU {r}", 24), math_tex(f"E_{r}", size=30, color=colors[r])).arrange(RIGHT, buff=.24).move_to([-5.5, y, 0])
            self.add(gpu, Line([-4.15, y-.40, 0], [6.30, y-.40, 0], color="#33465A"))
            row = VGroup(*[RoundedRectangle(width=.48, height=.48, corner_radius=.05,
                          stroke_width=0, fill_color=colors[r], fill_opacity=1)
                          .move_to([-3.65+j*.55, y, 0]) for j in range(12 if r==0 else 4)])
            rows.append(row)
            counts.append(math_tex(fr"\ell_{r}", "=", "12" if r==0 else "4", size=31, color=colors[r]).move_to([5.45,y,0]))
        self.add(prose("weights", 22, MUTED).move_to([3.70, 1.99, 0]))
        owner = weight_badge([3.70, ys[0], 0])
        slots = [panel(.88,.58,MUTED,[3.70,y,0],0) for y in ys[1:]]
        self.add(owner, *slots)
        maximum = math_tex(r"\max_r\ell_r", "=", "12", size=38, color=AMBER).move_to([-2.8,-2.88,0])
        total = math_tex(r"\sum_r\ell_r", "=", "24", size=36, color=TEAL).move_to([3.3,-2.88,0])
        caption = self.foot("The longest queue determines the compute load.")
        self.play(LaggedStart(*[FadeIn(row, shift=RIGHT*.15) for row in rows], lag_ratio=.18),
                  *[Write(c) for c in counts], Write(maximum), Write(total), FadeIn(caption), run_time=2)
        self.play(Circumscribe(rows[0], color=AMBER, buff=.12), Indicate(maximum, color=AMBER), run_time=1.5)
        self.wait(1.5)
        self.checkpoint("straggler and conserved total")
        new_caption = self.foot("First copy the weights; the token blocks stay put.")
        self.play(ReplacementTransform(caption,new_caption), run_time=.5); caption=new_caption
        replicas=[]
        for r in range(1,4):
            replica = weight_badge([3.70,ys[r],0]); replicas.append(replica)
            self.play(TransformFromCopy(owner,replica,path_arc=-.35), FadeOut(slots[r-1]), run_time=.85)
        self.wait(1)
        self.checkpoint("weights copied before work moves")
        new_caption=self.foot("Now move the existing blocks. Keep their expert identity.")
        self.play(ReplacementTransform(caption,new_caption),run_time=.5);caption=new_caption
        self.play(*[row.animate.set_opacity(.4) for row in rows[1:]],run_time=.4)
        for r in range(1,4):
            pair=rows[0][6+(r-1)*2:8+(r-1)*2]
            self.play(*[Indicate(block,color=INK,scale_factor=1.12) for block in pair],run_time=.5)
            donor=math_tex(r"\ell_0","=",str(12-r*2),size=31,color=AMBER).move_to(counts[0])
            receiver=math_tex(fr"\ell_{r}","=","6",size=31,color=colors[r]).move_to(counts[r])
            new_maximum=math_tex(r"\max_r\ell_r","=",str(12-r*2),size=38,color=TEAL if r==3 else AMBER).move_to(maximum)
            paths=[ArcBetweenPoints(block.get_center(),[-3.65+(4+j)*.55,ys[r],0],angle=-.30) for j,block in enumerate(pair)]
            self.play(*[MoveAlongPath(block,path) for block,path in zip(pair,paths)],
                      TransformMatchingTex(counts[0],donor),TransformMatchingTex(counts[r],receiver),
                      TransformMatchingTex(maximum,new_maximum),run_time=1.6)
            counts[0],counts[r]=donor,receiver
            maximum=new_maximum
            self.wait(.4)
        self.play(*[row.animate.set_opacity(1) for row in rows[1:]],run_time=.5)
        self.play(Indicate(maximum,color=TEAL),Circumscribe(total,color=TEAL,buff=.15),run_time=1.2)
        self.checkpoint("same blocks balanced across four GPUs")
        new_caption=self.foot("Block-load schematic. Copying weights also costs communication.")
        self.play(ReplacementTransform(caption,new_caption),run_time=.5)
        self.finish()


class ForwardPipeline(Base):
    def construct(self):
        self.heading("02", "Let readiness release the work", "Each projection waits for its own inputs.")
        fc1_eq=math_tex("Z","=","X","W_1",size=48).move_to([-4.1,.9,0])
        act_eq=math_tex("A","=",r"f(Z)",size=48).move_to([0,.9,0])
        fc2_eq=math_tex("O","=","A","W_2",size=48).move_to([4.1,.9,0])
        fc1_eq[3].set_color(AMBER);fc1_eq[2].set_color(TEAL)
        fc2_eq[3].set_color(AMBER);fc2_eq[2].set_color(TEAL)
        labels=VGroup(code_text("FC1",28,TEAL).move_to([-4.1,.05,0]),prose("activation",26,MUTED).move_to([0,.05,0]),code_text("FC2",28,BLUE).move_to([4.1,.05,0]))
        intro=prose("The weights belong to different phases.",29).move_to([0,-1.2,0])
        self.play(Write(fc1_eq),FadeIn(labels[0]),run_time=1.1)
        self.play(Write(act_eq),FadeIn(labels[1]),run_time=.9)
        self.play(Write(fc2_eq),FadeIn(labels[2]),FadeIn(intro),run_time=1.1)
        self.play(Indicate(fc1_eq[3],color=AMBER),Indicate(fc2_eq[3],color=AMBER),run_time=1)
        self.wait(1.2)
        self.checkpoint("projection equations with isolated weight symbols")
        top=VGroup(track("W_1",[-3.3,1.0,0],AMBER),track("W_2",[-1.1,1.0,0],AMBER),track("FC1",[1.1,1.0,0],TEAL,"code"),track("FC2",[3.3,1.0,0],BLUE,"code"))
        title=prose("Separate stages",25,MUTED).move_to([-4.8,1.83,0])
        self.play(FadeOut(intro),FadeOut(act_eq),
                  TransformFromCopy(fc1_eq[3],top[0].label),TransformFromCopy(fc2_eq[3],top[1].label),
                  TransformFromCopy(labels[0],top[2].label),TransformFromCopy(labels[2],top[3].label),
                  *[Create(t.shell) for t in top],run_time=1.4)
        self.remove(*[t.label for t in top],*[t.shell for t in top]);self.add(top)
        self.play(FadeOut(fc1_eq),FadeOut(fc2_eq),FadeOut(labels),FadeIn(title),run_time=.6)
        self.wait(1)
        pipe=VGroup(track("W_1",[-3.3,-.4,0],AMBER),track("W_2",[-1.1,-.4,0],AMBER),track("FC1",[-1.1,-1.4,0],TEAL,"code"),track("FC2",[1.1,-1.4,0],BLUE,"code"))
        transfer=prose("transfer",24,MUTED).move_to([-5.7,-.4,0])
        compute=prose("compute",24,MUTED).move_to([-5.7,-1.4,0])
        self.play(*[TransformFromCopy(a,b) for a,b in zip(top,pipe)],top.animate.set_opacity(.38),FadeIn(transfer),FadeIn(compute),run_time=1.6)
        self.remove(*pipe);self.add(pipe)
        cursor=Line([-4.4,.1,0],[-4.4,-1.88,0],color=INK,stroke_width=2)
        input_label=VGroup(math_tex("X",size=34,color=TEAL),prose("input ready",24,TEAL)).arrange(RIGHT,buff=.18).move_to([3.9,1.82,0])
        code1=readiness_code("W1","X","FC1",TEAL).move_to([-1.25,-2.72,0])
        footer=self.foot("Schematic time. An input block is already available.")
        self.play(Create(cursor),FadeIn(input_label),FadeIn(code1),FadeIn(footer),run_time=.8)
        self.play(GrowFromEdge(pipe[0].progress,LEFT),cursor.animate.shift(RIGHT*2.2),run_time=2.2,rate_func=linear)
        self.play(Circumscribe(pipe[0],color=AMBER),Indicate(input_label,color=TEAL),run_time=.8)
        self.wait(.7)
        self.checkpoint("first readiness gate opens")
        bracket=SurroundingRectangle(VGroup(pipe[1],pipe[2]),color=TEAL,buff=.10,corner_radius=.08)
        overlap=prose("same time",25,TEAL).move_to([2.7,-.4,0])
        # The two progress fills grow together: this is the dependency being taught.
        self.play(GrowFromEdge(pipe[1].progress,LEFT),GrowFromEdge(pipe[2].progress,LEFT),cursor.animate.shift(RIGHT*2.2),run_time=3,rate_func=linear)
        self.play(Create(bracket),FadeIn(overlap),run_time=.6)
        self.wait(1.2)
        self.checkpoint("W2 transfer and FC1 grow concurrently")
        self.play(FadeOut(bracket),FadeOut(overlap),run_time=.3)
        code2=readiness_code("W2","A","FC2",BLUE).move_to(code1)
        ready_note=VGroup(math_tex("A",size=34,color=TEAL),prose("activation ready",24,TEAL)).arrange(RIGHT,buff=.18).move_to(input_label)
        self.play(ReplacementTransform(code1,code2),ReplacementTransform(input_label,ready_note),Circumscribe(VGroup(pipe[1],pipe[2]),color=TEAL),run_time=1)
        self.play(GrowFromEdge(pipe[3].progress,LEFT),cursor.animate.shift(RIGHT*2.2),run_time=2.2,rate_func=linear)
        self.play(FadeOut(cursor),run_time=.4)
        note=prose("Start a phase when\nits dependencies arrive.",25,TEAL).move_to([4.1,-2.63,0])
        self.play(FadeIn(note),run_time=.5)
        self.finish()


class BackwardReduction(Base):
    def construct(self):
        self.heading("03", "The last partial opens the gate", "One gradient tile. Three participating copies.")
        xs,colors=[-4.4,0,4.4],[TEAL,BLUE,AMBER]
        values=[r"\begin{pmatrix}1&2\\0&1\end{pmatrix}",r"\begin{pmatrix}0&1\\3&0\end{pmatrix}",r"\begin{pmatrix}2&0\\1&1\end{pmatrix}"]
        cards,matrices,dots,states=[],[],[],[]
        for r,(x,c) in enumerate(zip(xs,colors)):
            self.add(prose(["Owner","Replica A","Replica B"][r],27).move_to([x,1.99,0]))
            shell=panel(3.2,2.2,c,[x,.55,0])
            symbol=math_tex(fr"G_0^{{({r})}}",size=34,color=c).move_to([x,1.30,0])
            matrix=math_tex(values[r],size=43,color=c).move_to([x,.45,0])
            dot=Dot([x+1.28,1.42,0],color=MUTED,radius=.075)
            state=prose("waiting",22,MUTED).move_to([x,-.36,0])
            cards.append(VGroup(shell,symbol));matrices.append(matrix);dots.append(dot);states.append(state)
        self.play(*[FadeIn(c) for c in cards],*[FadeIn(x) for x in dots+states],run_time=1)
        equation=math_tex(r"dW_0","=",r"G_0^{(0)}","+",r"G_0^{(1)}","+",r"G_0^{(2)}",size=36).move_to([0,-2.9,0])
        for i,c in zip([2,4,6],colors):equation[i].set_color(c)
        self.play(Write(equation),run_time=1)
        for r in [0,1]:
            ready=prose("ready",22,colors[r]).move_to(states[r])
            self.play(Write(matrices[r]),dots[r].animate.set_color(colors[r]),ReplacementTransform(states[r],ready),run_time=1)
            states[r]=ready
        missing=prose("Two partials are ready.\nThe last one still blocks reduction.",29).move_to([0,-1.55,0])
        self.play(FadeIn(missing),Circumscribe(cards[2],color=AMBER,buff=.1),run_time=1)
        self.wait(2)
        self.checkpoint("reduction blocked on replica B")
        ready=prose("ready",22,AMBER).move_to(states[2])
        all_ready=prose("All three partials are ready.\nNow the owner can reduce this tile.",29,TEAL).move_to(missing)
        self.play(Write(matrices[2]),dots[2].animate.set_color(AMBER),ReplacementTransform(states[2],ready),ReplacementTransform(missing,all_ready),run_time=1.2)
        missing=all_ready
        self.play(Indicate(equation[6],color=AMBER),run_time=.8)
        self.wait(.8)
        accumulator=math_tex(r"\begin{pmatrix}0&0\\0&0\end{pmatrix}",size=46,color=VIOLET).move_to([0,-1.5,0])
        accbox=panel(2.75,1.25,VIOLET,[0,-1.5,0])
        owner_note=prose("Owner accumulates\nin a fixed order",25).move_to([-4.4,-1.5,0])
        next_note=prose("Later tiles compute",23,BLUE).move_to([4.4,-.94,0])
        shells=VGroup(*[panel(2.5,.18,BLUE,[4.4,-1.4-i*.32,0],0) for i in range(3)])
        fills=VGroup(*[Rectangle(width=.02,height=.12,stroke_width=0,fill_color=BLUE,fill_opacity=.8).align_to(s,LEFT).shift(RIGHT*.035).set_y(s.get_y()) for s in shells])
        self.play(FadeOut(missing),Create(accbox),Write(accumulator),FadeIn(owner_note),FadeIn(next_note),FadeIn(shells),FadeIn(fills),run_time=1)
        self.checkpoint("all producers ready before accumulation")
        sums=[r"\begin{pmatrix}1&2\\0&1\end{pmatrix}",r"\begin{pmatrix}1&3\\3&1\end{pmatrix}",r"\begin{pmatrix}3&3\\4&2\end{pmatrix}"]
        for r in range(3):
            moving=matrices[r].copy().scale(.65)
            self.add(moving)
            destination=[-2.0,-1.5,0]
            path=ArcBetweenPoints(moving.get_center(),destination,angle=.3 if r<2 else -.3)
            next_sum=math_tex(sums[r],size=46,color=VIOLET).move_to(accumulator)
            self.play(MoveAlongPath(moving,path),Indicate(equation[2+r*2],color=colors[r]),
                      *[f.animate.stretch_to_fit_width(2.4*(r+1)/3).align_to(s,LEFT).shift(RIGHT*.035) for f,s in zip(fills,shells)],run_time=1.6,rate_func=smooth)
            self.play(FadeOut(moving,scale=.7),TransformMatchingTex(accumulator,next_sum),run_time=.6)
            accumulator=next_sum
            self.wait(.35)
        self.play(Circumscribe(accbox,color=VIOLET),run_time=.9)
        self.add(self.foot("Illustrative 2 × 2 values. Reduction overlaps later computation."))
        self.checkpoint("three partials accumulated while later tiles progress")
        self.finish()
