"""Generate the USB/3.3 V bench with eight LEDs moved between two registers."""
from pathlib import Path
from kicad_drawing import Drawing, line, rectangle, write_library_table

HERE = Path(__file__).resolve().parent
d = Drawing("heating_controller_logic_bench", "HeatingBench")
d.define("R", "R", [(1,"",-5.08,0,0),(2,"",5.08,0,180)], rectangle(-2.54,1.016,2.54,-1.016))
d.define("LED", "D", [(1,"K",-5.08,0,0),(2,"A",5.08,0,180)],
            line(-1.27,-1.27,-1.27,1.27) +
            '(polyline (pts (xy -1.27 0) (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0)) '
            '(stroke (width 0) (type default)) (fill (type none)))' +
            line(0,1.27,-1.27,2.54) + line(1.27,2.54,0,3.81))
d.define("C", "C", [(1,"",-5.08,0,0),(2,"",5.08,0,180)],
            line(-0.635,-2.54,-0.635,2.54) + line(0.635,-2.54,0.635,2.54) +
            line(-2.54,0,-0.635,0) + line(0.635,0,2.54,0))
d.define("Cpol", "C", [(1,"+",-5.08,0,0),(2,"-",5.08,0,180)],
            line(-0.635,-2.54,-0.635,2.54) + line(0.635,-2.54,0.635,2.54) +
            line(-2.54,0,-0.635,0) + line(0.635,0,2.54,0))
d.define("Switch", "S", [(1,"",-5.08,0,0),(2,"",5.08,0,180)], line(-2.54,0,2.54,2.54))
d.define("Conn6", "J", [(i+1,"",7.62,-i*2.54,180) for i in range(6)], rectangle(-2.54,2.54,5.08,-15.24))
d.define("Conn8", "J", [(i+1,"",7.62,-i*10.16,180) for i in range(8)], rectangle(-2.54,2.54,5.08,-73.66))
outputs = [(15, "QA"), (1,"QB"), (2,"QC"), (3,"QD"), (4,"QE"), (5,"QF"), (6,"QG"), (7,"QH")]
inputs = [(14,"SER"), (11,"SRCLK"), (12,"RCLK"), (10,"SRCLR_N"), (13,"OE_N"), (16,"VCC"), (8,"GND"), (9,"QH_PRIME")]
d.define("HC595", "U", [(pin,name,-22.86,30.48-i*10.16,0) for i,(pin,name) in enumerate(inputs)] +
            [(pin,name,22.86,30.48-i*10.16,180) for i,(pin,name) in enumerate(outputs)],
            rectangle(-20.32,35.56,20.32,-45.72))

d.text("BANC LED - USB / 3,3 V UNIQUEMENT - AUCUN FIL PILOTE NI SECTEUR", 20.32,15.24,2)
d.text("GPIO10 = inhibition OE_N directe. Ce banc ne valide pas le watchdog ni les superviseurs de l'etude C.",20.32,22.86)
d.text("Alimenter les registres depuis 3V3 de la DevKit. Ne pas utiliser 5 V sur ces registres ou les GPIO.",20.32,30.48)

for chip,y in ((1,85.09),(2,187.96)):
    d.symbol("HC595",f"U{chip}","SN74HC595N / 3V3",76.2,y,title_offset=43.18)
    d.symbol("Conn8",f"JOUT{chip}",f"U{chip} : QA a QH",139.7,y-30.48)
    nets = ["DATA" if chip == 1 else "CASCADE", "CLOCK", "LATCH",
            "+3V3", "OE_N", "+3V3", "GND_TBT", "CASCADE"]
    for i,net in enumerate(nets):
        yy = y-30.48+i*10.16
        if i == 7 and chip == 2:
            d.no_connect(53.34,yy)
        else:
            d.wire(43.18,yy,53.34,yy)
            d.label(net,43.18,yy)
    for i,(_,output) in enumerate(outputs):
        yy = y-30.48+i*10.16
        net = f"U{chip}_{output}"
        d.wire(99.06,yy,109.22,yy)
        d.label(net,109.22,yy)
        d.wire(147.32,yy,157.48,yy)
        d.label(net,157.48,yy)
    d.symbol("C",f"C{chip}","100nF",22.86,y+7.62)
    d.wire(12.7,y+7.62,17.78,y+7.62)
    d.label("+3V3",12.7,y+7.62)
    d.wire(27.94,y+7.62,33.02,y+7.62)
    d.label("GND_TBT",33.02,y+7.62)

d.symbol("Conn8","JLED1","Bloc 4 paires / entree 1 a 8",208.28,54.61)
for i in range(8):
    yy = 54.61+i*10.16
    d.wire(215.9,yy,248.92,yy)
    d.symbol("R",f"R{i+1}","2k2 / 1%",254,yy,title_offset=5.08)
    d.wire(259.08,yy,287.02,yy)
    value = f"P{i//2+1} {'+ ROUGE' if i%2==0 else '- VERTE'}"
    d.symbol("LED",f"D{i+1}",value,292.1,yy,180,title_offset=5.08)
    d.wire(297.18,yy,317.5,yy)
    d.label("GND_TBT",317.5,yy)
d.text("HORS TENSION : relier JLED1 1..8 a JOUT1 OU JOUT2 1..8.",208.28,139.7,1.3)
d.text("JLED1 sur JOUT1 OU JOUT2. Ne jamais relier JOUT1 et JOUT2 ensemble.",208.28,146.05,1.3)
d.text("JOUT1 : FP1..FP4 ; JOUT2 : FP5..FP8. GND = GND_TBT.",208.28,152.4,1.3)

d.symbol("Conn6","JH1","Interface DevKit",355.6,50.8)
for i,net in enumerate(("+3V3","GND_TBT","DATA","CLOCK","LATCH","BENCH_OE_N")):
    d.wire(363.22,50.8+i*2.54,378.46,50.8+i*2.54)
    d.label(net,378.46,50.8+i*2.54)

d.text("INHIBITION DU BANC",208.28,171.45,1.7)
for ref,value,left,right,y in (("R17","1k","BENCH_OE_N","OE_N",187.96),
                                ("R18","10k","+3V3","OE_N",205.74)):
    d.symbol("R",ref,value,248.92,y)
    d.wire(208.28,y,243.84,y); d.label(left,208.28,y)
    d.wire(254,y,269.24,y); d.label(right,269.24,y)
d.symbol("Switch","S1","Poussoir / appui = INHIBER",248.92,223.52)
d.wire(208.28,223.52,243.84,223.52); d.label("+3V3",208.28,223.52)
d.wire(254,223.52,269.24,223.52); d.label("OE_N",269.24,223.52)
d.text("R17 limite le courant pendant l'appui sur S1",208.28,236.22,1.2)
d.text("alors que GPIO10 commande un niveau bas.",208.28,241.3,1.2)

for idx,(net,y) in enumerate((("DATA",177.8),("CLOCK",195.58),("LATCH",213.36)),19):
    d.symbol("R",f"R{idx}","10k",355.6,y)
    d.wire(335.28,y,350.52,y); d.label(net,335.28,y)
    d.wire(360.68,y,375.92,y); d.label("GND_TBT",375.92,y)

d.symbol("Cpol","C3","10uF / 35V ou 50V",355.6,233.68)
d.wire(335.28,233.68,350.52,233.68); d.label("+3V3",335.28,233.68)
d.wire(360.68,233.68,375.92,233.68); d.label("GND_TBT",375.92,233.68)
d.text("JH1 : 1=3V3, 2=GND, 3=GPIO0, 4=GPIO1, 5=GPIO22, 6=GPIO10",20.32,254,1.5)
d.text("S1 en appui au premier demarrage. Inhibition logicielle au boot ; activation manuelle dans Home Assistant.",20.32,261.62,1.3)
d.text("Huit LED : 4 rouges (+) et 4 vertes (-), chacune avec sa resistance. Observation des 16 sorties en deux passes.",20.32,269.24,1.3)
d.save(HERE,"Heating controller - banc 4 paires LED / TBT uniquement", date="2026-11-01", revision="E-banc-TBT")
write_library_table(HERE)
