"""Generate the USB/3.3 V-only two-register, sixteen-LED bench schematic."""
from pathlib import Path
from kicad_drawing import Drawing, line, rectangle

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
outputs = [(15, "QA"), (1,"QB"), (2,"QC"), (3,"QD"), (4,"QE"), (5,"QF"), (6,"QG"), (7,"QH")]
inputs = [(14,"SER"), (11,"SRCLK"), (12,"RCLK"), (10,"SRCLR_N"), (13,"OE_N"), (16,"VCC"), (8,"GND"), (9,"QH_PRIME")]
d.define("AHC595", "U", [(pin,name,-22.86,30.48-i*10.16,0) for i,(pin,name) in enumerate(inputs)] +
            [(pin,name,22.86,30.48-i*10.16,180) for i,(pin,name) in enumerate(outputs)],
            rectangle(-20.32,35.56,20.32,-45.72))

d.text("BANC LED - USB / 3,3 V UNIQUEMENT - AUCUN FIL PILOTE NI SECTEUR", 20.32,15.24,2)
d.text("GPIO10 = inhibition OE_N directe. Ce banc ne valide pas le watchdog ni les superviseurs de l'etude C.",20.32,22.86)
d.text("Alimenter les registres depuis 3V3 de la DevKit. Ne pas utiliser 5 V sur ces registres ou les GPIO.",20.32,30.48)

for chip,y in ((1,85.09),(2,187.96)):
    d.symbol("AHC595",f"U{chip}","SN74AHC595N / 3V3",127,y,title_offset=43.18)
    nets = ["DATA" if chip == 1 else "CASCADE", "CLOCK", "LATCH", "+3V3", "OE_N", "+3V3", "GND_TBT", "CASCADE"]
    for i,net in enumerate(nets):
        yy = y-30.48+i*10.16
        if i == 7 and chip == 2:
            d.no_connect(104.14,yy)
        else:
            d.wire(93.98,yy,104.14,yy)
            d.label(net,93.98,yy)
    for i,(pin,_) in enumerate(outputs):
        yy = y-30.48+i*10.16
        number = (chip-1)*8+i
        d.wire(149.86,yy,174.0,yy)
        d.symbol("R",f"R{number+1}","2k2 / 1%",179.08,yy,title_offset=5.08)
        d.wire(184.16,yy,204.28,yy)
        d.symbol("LED",f"D{number+1}",f"FP{number//2+1} {'+' if number%2==0 else '-'}",209.36,yy,180,title_offset=5.08)
        d.wire(214.44,yy,229.68,yy)
        d.label("GND_TBT",229.68,yy)
    # Local ceramic decoupling, each pin separately labelled.
    d.symbol("C",f"C{chip}","100nF ceramique",60.96,y+7.62,title_offset=7.62)
    d.wire(45.72,y+7.62,55.88,y+7.62)
    d.label("+3V3",45.72,y+7.62)
    d.wire(66.04,y+7.62,76.2,y+7.62)
    d.label("GND_TBT",76.2,y+7.62)

d.symbol("Conn6","JH1","Interface DevKit / voir table",297.18,50.8)
for i,net in enumerate(("+3V3","GND_TBT","DATA","CLOCK","LATCH","BENCH_OE_N")):
    d.wire(304.8,50.8+i*2.54,320.04,50.8+i*2.54)
    d.label(net,320.04,50.8+i*2.54)

d.text("INHIBITION DU BANC",274.32,88.9,1.7)
for ref,value,left,right,y in (("R17","1k","BENCH_OE_N","OE_N",104.14),
                                ("R18","10k","+3V3","OE_N",121.92)):
    d.symbol("R",ref,value,299.72,y)
    d.wire(279.4,y,294.64,y); d.label(left,279.4,y)
    d.wire(304.8,y,320.04,y); d.label(right,320.04,y)
d.symbol("Switch","S1","Fermer = INHIBER",299.72,139.7)
d.wire(279.4,139.7,294.64,139.7); d.label("+3V3",279.4,139.7)
d.wire(304.8,139.7,320.04,139.7); d.label("OE_N",320.04,139.7)
d.text("R17 limite le courant si S1 est ferme",269.24,152.4,1.2)
d.text("alors que GPIO10 commande un niveau bas.",269.24,157.48,1.2)

for idx,(net,y) in enumerate((("DATA",177.8),("CLOCK",195.58),("LATCH",213.36)),19):
    d.symbol("R",f"R{idx}","10k",299.72,y)
    d.wire(279.4,y,294.64,y); d.label(net,279.4,y)
    d.wire(304.8,y,320.04,y); d.label("GND_TBT",320.04,y)

d.symbol("Cpol","C3","10uF / 35V ou 50V",299.72,233.68)
d.wire(279.4,233.68,294.64,233.68); d.label("+3V3",279.4,233.68)
d.wire(304.8,233.68,320.04,233.68); d.label("GND_TBT",320.04,233.68)
d.text("JH1 : 1=3V3, 2=GND, 3=GPIO0, 4=GPIO1, 5=GPIO22, 6=GPIO10",20.32,254,1.5)
d.text("Fermer S1 avant mise sous tension. Registres inhibes au demarrage ; activation manuelle dans Home Assistant.",20.32,261.62,1.3)
d.text("Seize LED d'indication rouge basse consommation, chacune avec sa resistance. Aucun retour de mesure des sorties.",20.32,269.24,1.3)
d.save(HERE,"Heating controller - banc 16 LED / TBT uniquement")
(HERE / "sym-lib-table").write_text('''(sym_lib_table (version 7)
    (lib (name "Heating") (type "KiCad") (uri "${KIPRJMOD}/Heating.kicad_sym") (options "") (descr "Provisional heating module symbols"))
    (lib (name "HeatingBench") (type "KiCad") (uri "${KIPRJMOD}/HeatingBench.kicad_sym") (options "") (descr "USB LED bench symbols")))
''')
