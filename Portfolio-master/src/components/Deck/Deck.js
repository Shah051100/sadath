import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./Deck.css";

const Icon = ({ name, size = 20, stroke = "currentColor", fill = "none" }) => {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill,
    stroke,
    strokeWidth: 1.7,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true,
  };

  const paths = {
    land: (
      <>
        <path d="M3 20h18" />
        <path d="m4 17 5-6 3 3 3-5 5 8" />
        <path d="M7 20v-3m10 3v-5" />
      </>
    ),
    loss: (
      <>
        <path d="M12 3 3.7 19h16.6L12 3Z" />
        <path d="M12 9v4m0 3h.01" />
      </>
    ),
    factory: (
      <>
        <path d="M3 21h18M4 21V10l6 3V9l6 4V6h4v15" />
        <path d="M8 17h.01M12 17h.01M17 17h.01" />
      </>
    ),
    disconnect: (
      <>
        <path d="m8 12 3-3 2 2-3 3-2-2Zm5-5 2-2 3 3-2 2m-7 7-2 2-3-3 2-2m9-4 3-3m-7 7-3 3" />
      </>
    ),
    apple: (
      <>
        <path d="M12 8c-3-4-8-1-8 4 0 5 3 9 8 9s8-4 8-9c0-5-5-8-8-4Z" />
        <path d="M12 8c0-3 2-5 5-5-1 3-3 4-5 5Z" />
      </>
    ),
    leaf: <path d="M20 4C10 4 4 8 4 16c0 2 1 4 1 4s2-1 4-1c7 0 10-5 11-15ZM5 20c3-5 7-8 12-11" />,
    sheep: (
      <>
        <path d="M7 15a4 4 0 1 1 4-6 4 4 0 1 1 5 5c0 3-2 5-5 5s-4-1-4-4Z" />
        <path d="M16 13h3l2 2-2 2h-3M8 19v2m7-2v2" />
      </>
    ),
    chicken: (
      <>
        <path d="M6 16c0-4 3-7 7-7 4 0 6 3 6 6 0 3-2 5-6 5H8c-2 0-3-2-2-4Z" />
        <path d="M17 9c1-2 3-2 4-1M8 8c-1-2 0-4 2-4 1 1 1 2 0 3M19 14h2m-9 6v2m-5-2v2" />
      </>
    ),
    fish: (
      <>
        <path d="M3 12s4-6 10-6c4 0 7 3 8 6-1 3-4 6-8 6-6 0-10-6-10-6Z" />
        <path d="m3 12-2-3 4 1m-4 5 4-1m7-3h.01" />
      </>
    ),
    compost: (
      <>
        <path d="M5 10h14l-1 10H6L5 10Z" />
        <path d="M8 10c0-3 2-5 4-5s4 2 4 5M12 5V3m-4 4L6 5m10 2 2-2" />
      </>
    ),
    water: (
      <>
        <path d="M12 3s6 6 6 11a6 6 0 0 1-12 0c0-5 6-11 6-11Z" />
        <path d="M9 16c1 2 3 2 4 2" />
      </>
    ),
    solar: (
      <>
        <path d="m4 10 16 4-2 7H2l2-11Z" />
        <path d="m8 12-1 9m6-7-1 7m6-6-1 6M4 4V2m5 3L8 3m8 4 2-2m0 6h3" />
      </>
    ),
    box: (
      <>
        <path d="m4 7 8-4 8 4-8 4-8-4Zm0 0v10l8 4 8-4V7m-8 4v10" />
      </>
    ),
    arrow: <path d="M4 12h15m-5-5 5 5-5 5" />,
    check: <path d="m5 12 4 4L19 6" />,
    pin: (
      <>
        <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" />
        <circle cx="12" cy="10" r="2.5" />
      </>
    ),
    flask: (
      <>
        <path d="M9 3h6m-5 0v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3" />
        <path d="M7 16h10" />
      </>
    ),
    chart: (
      <>
        <path d="M4 19V5m0 14h17" />
        <path d="m7 15 4-4 3 2 5-7" />
      </>
    ),
    camera: (
      <>
        <path d="M4 7h4l1.5-2h5L16 7h4v12H4V7Z" />
        <circle cx="12" cy="13" r="3.3" />
      </>
    ),
    plus: <path d="M12 5v14M5 12h14" />,
  };

  return <svg {...common}>{paths[name] || paths.leaf}</svg>;
};

const notes = [
  `Good morning. My name is Saadat. I'm a Food Technology graduate from IUST Kashmir and a RISE UP Sustainable Kashmir Fellow. I'm here to present an integrated farming model that I want to build and prove on my family's 7-kanal farm in Mattan, Anantnag. The core idea is simple: instead of running separate farm activities that waste resources and capture low value, I want to connect horticulture, livestock, poultry, aquaculture, composting, and food processing into one circular system where every output becomes another system's input. The goal is not to build the biggest farm in Kashmir. It is to build the smartest small farm I can — and then test whether the model can be replicated with other smallholder farmers across the valley.`,
  `Kashmir's agriculture employs roughly 43% of the workforce and contributes about 20% of GSVA. But the system leaks value at every step. The average landholding is around 12 kanals — my family has 7. That means most farmers simply cannot grow their way to higher income by adding more land. They need to get more from what they already have. NITI Aayog's 2026 horticulture roadmap confirms that post-harvest losses run 20 to 30 percent, and that less than 1% of J&K's fruit output is processed. That means the value addition — the grading, drying, packaging, branding — happens somewhere else, or doesn't happen at all. On top of that, most farms manage their crops, animals, water, and waste as separate activities. Crop residues are burned. Manure is discarded. Water flows through once and leaves. The problem is not that Kashmir can't grow food. It's that the current model captures only a fraction of the value that the land could produce.`,
  `Today, a typical Kashmir farmer runs separate activities. They grow apples. Maybe they keep a few sheep. They buy fertilizer, buy feed, buy fuel. Waste is a problem to dispose of, not a resource to use. Produce is sold raw at the local mandi, and the processing margin goes to someone else. Technology, when it appears, is often expensive and imported. My proposed model changes the architecture, not just the crops. Instead of separate enterprises, I connect them. Crop residues become compost and fodder. Animal manure becomes compost and eventually biogas feedstock. Rainwater is harvested. Solar powers pumps. And Food Technology expertise adds a processing layer that captures value on-farm. From a cost perspective, this means shared infrastructure instead of duplicated spending, internal resource cycling instead of purchased inputs, and phased investment instead of building everything at once. On the technology spectrum, I'm not proposing low-tech subsistence farming, and I'm not proposing an expensive automated vertical farm. I'm positioning in the middle: appropriate technology. Solar, drip irrigation, modular hydroponic fodder, water quality monitoring, controlled composting — all locally serviceable, all chosen because they lower cost or improve control, not because they look impressive.`,
  `This is the system I want to build and prove. At the top, horticulture — my existing apple and walnut orchards, plus vegetables and selected high-value crops. Crop residues and pruning waste flow into composting and fodder production. Livestock and poultry generate manure and litter, which also flow into composting and eventually biogas when feedstock is sufficient. Compost returns to the soil, reducing purchased fertilizer. Rainwater and canal water are managed through storage and efficient irrigation. Solar powers pumps and basic controls. And at the bottom, the value addition layer — grading, drying, processing, packaging — which is where my Food Technology background becomes the differentiator. Every output becomes another system's input. I want to be clear about one thing: trout is a proposed pilot, not a guaranteed component. It will only be added after water quality testing confirms suitable temperature, dissolved oxygen, and flow. And all waste streams are physically separated — no raw manure enters fish water. The innovation here is not any single technology. It is the system architecture.`,
  `Why am I the right person to test this model? First, I'm not starting from zero. My family already has 7-plus kanals of land in Mattan with mature apple and walnut orchards, a vegetable garden, canal and borewell water access, and existing farm infrastructure. I don't need to acquire land. I don't need to plant trees and wait five years. The base is already there. Second, I have a B.Tech in Food Technology from IUST, which means I understand processing, food safety, quality control, and product development — the exact skills needed for the value-addition layer that most farms lack. Third, through the RISE UP fellowship, I've been actively studying permaculture, integrated farming, and sustainable agriculture in the Kashmir context. And fourth, I've already done the research. I have a working business plan backed by SKUAST-K, ICAR, and NITI Aayog data. I have site measurements. I have field visits planned to KVK Kulgam, SKUAST-K, and Khorasan Food Processing. I'm combining what I already have with what I already know.`,
  `This is the long-term architectural vision for the farm complex at the far end of my property. It's a multi-level structure built around the trout raceway zone. Ground level holds four proposed raceways — again, conditional on water testing. Level 1 is sheep housing with proper ventilation, drainage, and manure collection. Level 2 is poultry, with separate zones for desi birds and broilers. Level 3 is a small modular hydroponic fodder unit — not a giant vertical farm, just enough to supplement livestock feed. The roof carries solar panels and rainwater collection. On the side, water management, solids handling, and composting. Four flow lines — water, feed, waste, energy — run through the building but are physically separated. I want to be very clear: this is a conceptual design, not a construction-ready blueprint. It requires structural engineering, waterproofing validation, and regulatory approval. And it is a Phase 3 to 4 vision. In Phase 1, I'm not building this. I'm starting with what already exists and proving the model at ground level first.`,
  `Let me explain the economic logic. Today, a typical Kashmir farm on 7–12 kanals grows one or two crops, sells them raw, and loses the processing margin to middlemen. Input costs are high because everything is purchased externally. Waste has zero value — it's a disposal problem. My model changes three economic levers simultaneously. First, more output per kanal through diversification — instead of one crop, the farm produces fruit, vegetables, eggs, meat, honey, and eventually processed products. Second, lower input costs through internal resource cycling — compost replaces some fertilizer, hydroponic fodder supplements feed, rainwater reduces irrigation costs, solar reduces energy costs. Third, more value captured after production — instead of selling raw apples at mandi prices, the farm grades, dries, processes, and packages, capturing the margin that currently leaves the region. Compared to a traditional farm, this model offers more revenue streams, lower input dependence, waste-to-value conversion, and on-farm processing. I want to be honest: these are hypotheses, not proven numbers. The entire purpose of Phase 1 is to test whether this economic logic actually holds on my specific site with my specific resources. But the ICAR-documented integrated farm in Kashmir that reached 19 lakh annual family income gives me confidence that the direction is right.`,
  `My market strategy is a ladder, not a leap. I'm not starting by trying to sell branded Kashmiri products in Delhi. I'm starting with the customers I can serve well right now: local households in Mattan and Anantnag, and small hospitality businesses — hotels, houseboats, restaurants that want fresh, local, traceable produce. These customers have repeat demand, short delivery distances, and they give fast feedback. As the farm proves itself, I move up the ladder: graded and packed produce, then processed products like dried fruits, apple chips, walnut oil, honey, and eventually branded packaged goods. The final stage is farmer aggregation — sourcing from partner farmers and processing through shared infrastructure. For Phase 1, my revenue target is 5 to 10 lakh rupees annually from the existing orchard, vegetables, a small poultry unit, and beekeeping. The key cost drivers are feed, labour, irrigation, and inputs. The margin improvement comes from reducing waste and selling direct instead of through the mandi. These are pilot assumptions, not guarantees. The purpose of Phase 1 is to test these numbers against reality. But the logic is sound: start with customers I can learn from, then expand as the data supports it.`,
  `My go-to-market plan follows five phases, and the most important principle is that every phase must earn the right to become the next phase. Phase 1, starting now through 2027, is about proving the model on my existing land. Soil and water testing, orchard optimization, vegetables, a small poultry unit, beekeeping, composting, and my first local customers. Target revenue: 5 to 10 lakh. Phase 2 adds sheep, a greenhouse, hydroponic fodder, and potentially trout if water testing supports it. Phase 3 is where Food Technology becomes the differentiator — micro food processing, packaging, branding, and direct-to-consumer channels. This is where PMFME's 35% subsidy becomes relevant. Phase 4 is aggregation — partnering with other farmers, sharing processing infrastructure, and becoming a demonstration hub. Phase 5 is scale. I'm not building all of this at once. I'm also not doing this alone. The ecosystem I'm plugging into includes SKUAST-K and KVK for technical guidance, the J&K Agriculture and Fisheries departments for subsidies and validation, PMFME for processing support, StartupJK and JKEDI for incubation, DIC Anantnag for the local processing ecosystem, and eventually local SHGs and FPOs for farmer aggregation. The model is designed to fit into the existing institutional landscape, not to compete with it.`,
  `I want to close with three things. First, validation. I have a clear measurement plan across technical, commercial, and operational dimensions for every year from 2026 to 2030. In Year 1, I'm testing soil, water, crop performance, poultry mortality, first revenue, and customer feedback. In Year 2, I'm validating trout water quality, fodder yields, and repeat customer margins. In Year 3, I'm testing processing trials, shelf life, and quality. In Year 4, I'm measuring farmer pilot data and aggregation logistics. Every number will be tracked. Every assumption will be tested. Second, climate impact. Beyond economics, this model has real environmental benefits. Composting replaces waste burning. Organic inputs reduce chemical dependence. Rainwater harvesting and drip irrigation improve water efficiency. Preserving existing orchards maintains carbon sequestration. Mixed cropping and pollinator habitats support biodiversity. These are directional estimates — a formal lifecycle assessment will come in Phase 2 — but the direction is clear. Third, and most importantly, my mission. My long-term vision is a 5-crore-rupee annual business that creates livelihoods for 5,000 families. But I want to be very clear: that is a 2030 vision, not a current claim. I don't need to prove the whole vision today. I need to prove the first piece. One farm. Seven kanals. One year. Real data. If the model works, it can be replicated. If it doesn't, I'll learn why and adjust. That is the ask I'm bringing to JKEDI: not funding for a grand vision, but the mentorship, incubation, and technical support to prove the first small version of it. Thank you.`,
];

const phases = [
  {
    phase: "01",
    years: "2026–27",
    name: "PROVE",
    tone: "active",
    body: "Site survey · Soil/water testing · Orchard optimization · Vegetables · Small poultry (50–100) · Bees (5–10 hives) · Composting · First local customers",
    target: "Target: ₹5–10L revenue",
  },
  {
    phase: "02",
    years: "2027–28",
    name: "SELL + REPEAT",
    tone: "next",
    body: "Sheep (20–30) · Greenhouse · Hydroponic fodder · Pilot trout (if water validates) · Solar · Repeat hospitality customers · Track margins",
  },
  {
    phase: "03",
    years: "2028–29",
    name: "VALUE",
    tone: "future",
    body: "Micro food processing (PMFME-eligible) · Grading · Drying · Packaging · Branding · D2C channels",
  },
  {
    phase: "04",
    years: "2029–30",
    name: "AGGREGATE",
    tone: "future",
    body: "Partner farmers · Shared processing · Shared market access · Demonstration hub",
  },
  {
    phase: "05",
    years: "2030+",
    name: "SCALE",
    tone: "future",
    body: "Farmer network · Regional markets · Livelihood impact · Replication",
  },
];

function PhotoSlot({ slot, label, photo, onUpload, className = "" }) {
  return (
    <label className={`photo-slot ${className} ${photo ? "has-photo" : ""}`}>
      {photo ? (
        <img src={photo} alt={label} />
      ) : (
        <div className="photo-empty">
          <span className="photo-icon"><Icon name="camera" size={24} /></span>
          <strong>ADD REAL PHOTO</strong>
          <span>{label}</span>
        </div>
      )}
      <span className="photo-edit"><Icon name={photo ? "camera" : "plus"} size={13} /> {photo ? "Change" : "Upload"}</span>
      <input type="file" accept="image/*" onChange={(event) => onUpload(slot, event)} />
    </label>
  );
}

function SlideTop({ number, eyebrow, title, intro, dark = false, children }) {
  return (
    <>
      <div className="slide-top">
        <div className="slide-eyebrow">{eyebrow}</div>
        <div className={`slide-number ${dark ? "slide-number-dark" : ""}`}>{String(number).padStart(2, "0")}</div>
      </div>
      <h1 className="slide-title">{title}</h1>
      {intro && <p className="slide-intro">{intro}</p>}
      {children}
    </>
  );
}

function Source({ children }) {
  return <div className="source">Source · {children}</div>;
}

function MetricIcon({ type }) {
  return <span className={`metric-icon metric-${type}`}><Icon name={type} size={23} /></span>;
}

function SlideOne({ photo, onUpload }) {
  return (
    <section className="deck-slide cover-slide">
      <div className="cover-photo-layer" style={photo ? { backgroundImage: `linear-gradient(90deg, rgba(8, 37, 29, .82), rgba(8, 37, 29, .43)), url(${photo})` } : undefined} />
      <div className="cover-grain" />
      <div className="cover-content">
        <div className="cover-slide-number">01</div>
        <div className="cover-main">
          <div className="cover-title-block">
            <h1>KASHMIR<br /><em>INTEGRATED</em><br />FARM HUB</h1>
            <p className="cover-subtitle">A modular, circular farming model for higher value from small landholdings</p>
            <div className="cover-statement">One farm. Connected systems. <span>More value from the same land.</span></div>
          </div>
        </div>
        <div className="cover-bottom">
          <div>
            <strong>Mattan, Anantnag · Saadat</strong>
            <span>Food Technology × Permaculture × Appropriate Technology</span>
          </div>
          <div className="challenge-label">JKEDI<br /><span>STARTUP IDEA CHALLENGE 2.0</span></div>
        </div>
      </div>
      {!photo && (
        <PhotoSlot slot="cover" label="Mattan / Kashmir valley landscape" photo={photo} onUpload={onUpload} className="cover-upload" />
      )}
      {photo && <PhotoSlot slot="cover" label="Mattan / Kashmir valley landscape" photo={photo} onUpload={onUpload} className="cover-upload cover-upload-photo" />}
    </section>
  );
}

function SlideTwo({ photo, onUpload }) {
  const cards = [
    { icon: "land", value: "~12", unit: "kanals average landholding in J&K", desc: "Most farmers cannot scale horizontally", source: "Agriculture Census of India; J&K Economic Survey" },
    { icon: "loss", value: "20–30%", unit: "post-harvest losses in horticulture", desc: "Produce loses value before it reaches the buyer", source: "NITI Aayog J&K Horticulture Roadmap, 2026" },
    { icon: "factory", value: "<1%", unit: "of J&K fruit is processed", desc: "Raw produce leaves the farm; value leaves the region", source: "NITI Aayog; APEDA" },
    { icon: "disconnect", value: "Fragmented", unit: "systems", desc: "Crop, livestock, water, and waste managed separately", source: "ICAR-CSSRI integrated farming studies" },
  ];
  return (
    <section className="deck-slide paper-slide problem-slide">
      <SlideTop number={2} eyebrow="THE CASE FOR CHANGE" title="The problem isn’t only production. It’s value per kanal." />
      <div className="problem-grid">
        <div className="evidence-grid">
          {cards.map((card) => (
            <article className="evidence-card" key={card.unit}>
              <MetricIcon type={card.icon} />
              <div className="evidence-copy">
                <div className="evidence-value">{card.value}</div>
                <div className="evidence-unit">{card.unit}</div>
                <p>{card.desc}</p>
              </div>
              <Source>{card.source}</Source>
            </article>
          ))}
          <div className="problem-bottom">The opportunity is to increase value per kanal — not simply add more land.</div>
        </div>
        <div className="problem-photo-wrap">
          <PhotoSlot slot="problem" label="Kashmir farmer / mandi / harvest" photo={photo} onUpload={onUpload} />
          <div className="photo-note"><span>01</span> SHOW THE REALITY, NOT THE ASPIRATION</div>
        </div>
      </div>
    </section>
  );
}

function SlideThree() {
  const today = ["Separate enterprises, separate costs", "External inputs purchased repeatedly", "Waste handled as a disposal problem", "Raw produce sold at mandi prices", "Technology treated as an expense", "Investment before validation"];
  const proposed = ["Connected enterprises, shared infrastructure", "Internal resource cycling where practical", "Waste managed as a productive input", "Value addition before market where justified", "Technology selected for measurable cost benefit", "Pilot first, expand after evidence"];
  return (
    <section className="deck-slide paper-slide today-slide">
      <SlideTop number={3} eyebrow="THE SHIFT" title="From separate activities to one connected system." />
      <div className="compare-columns">
        <div className="compare-column today-column">
          <div className="compare-heading"><span>01</span><div><small>TODAY</small><strong>Linear farm</strong></div></div>
          <div className="compare-list">{today.map((item, i) => <div className="compare-item" key={item}><span>{String(i + 1).padStart(2, "0")}</span>{item}</div>)}</div>
        </div>
        <div className="compare-divider"><span>→</span></div>
        <div className="compare-column proposed-column">
          <div className="compare-heading"><span>02</span><div><small>PROPOSED</small><strong>Circular farm</strong></div></div>
          <div className="compare-list">{proposed.map((item, i) => <div className="compare-item" key={item}><span><Icon name="check" size={15} /></span>{item}</div>)}</div>
        </div>
      </div>
      <div className="tech-spectrum">
        <div className="spectrum-label">Technology position</div>
        <div className="spectrum-head"><span>LOW-TECH</span><span>APPROPRIATE TECH</span><span>EXPENSIVE HIGH-TECH</span></div>
        <div className="spectrum-track"><i /><i /><i /><b /></div>
        <div className="spectrum-notes"><span>Passive, manual</span><span>Solar · drip · compost · fodder · monitoring</span><span>Automation · imported systems · giant hydroponics</span></div>
        <div className="spectrum-pointer"><span>MY MODEL</span><i /></div>
      </div>
      <div className="bottom-thesis">The integrated approach shares infrastructure, recycles resources, and phases investment — lowering cost per unit of output.</div>
    </section>
  );
}

function FlowNode({ icon, label, detail, className }) {
  return (
    <div className={`flow-node ${className || ""}`}>
      <span className="flow-icon"><Icon name={icon} size={23} /></span>
      <strong>{label}</strong>
      <small>{detail}</small>
    </div>
  );
}

function SlideFour() {
  return (
    <section className="deck-slide paper-slide system-slide">
      <SlideTop number={4} eyebrow="THE SYSTEM MAP" title="One farm. Multiple connected outputs." />
      <div className="system-map">
        <svg className="system-lines" viewBox="0 0 900 360" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <marker id="greenArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10Z" fill="#2c7657" /></marker>
            <marker id="goldArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10Z" fill="#c48d43" /></marker>
          </defs>
          <path className="resource-line" d="M450 42 C365 48 290 72 236 120" markerEnd="url(#greenArrow)" />
          <path className="resource-line" d="M450 42 C535 48 610 72 664 120" markerEnd="url(#greenArrow)" />
          <path className="resource-line" d="M188 160 C205 220 270 260 350 282" markerEnd="url(#greenArrow)" />
          <path className="resource-line" d="M712 160 C695 220 630 260 550 282" markerEnd="url(#greenArrow)" />
          <path className="resource-line" d="M350 300 C400 325 500 325 550 300" markerEnd="url(#greenArrow)" />
          <path className="value-line" d="M450 103 C450 145 450 190 450 238" markerEnd="url(#goldArrow)" />
          <path className="value-line" d="M448 310 C448 327 448 337 448 349" markerEnd="url(#goldArrow)" />
        </svg>
        <div className="system-core"><span><Icon name="chart" size={25} /></span><strong>CIRCULAR<br />FARM HUB</strong><small>resource + value loops</small></div>
        <FlowNode icon="apple" label="HORTICULTURE" detail="Apple · walnut · vegetables" className="node-horticulture" />
        <FlowNode icon="sheep" label="LIVESTOCK" detail="Sheep · manure" className="node-livestock" />
        <FlowNode icon="leaf" label="VEGETABLES" detail="Seasonal · high-value" className="node-vegetables" />
        <FlowNode icon="chicken" label="POULTRY" detail="Desi · broiler" className="node-poultry" />
        <FlowNode icon="compost" label="COMPOST" detail="Vermicompost · biogas" className="node-compost" />
        <FlowNode icon="fish" label="AQUACULTURE" detail="Trout proposed" className="node-aqua" />
        <FlowNode icon="leaf" label="FODDER" detail="Hydroponic · solar" className="node-fodder" />
        <FlowNode icon="factory" label="VALUE ADDITION" detail="Grade · dry · process · package" className="node-value" />
        <div className="market-pill"><Icon name="box" size={16} /> MARKET</div>
        <div className="flow-label flow-label-1">crop residues → compost / fodder</div>
        <div className="flow-label flow-label-2">manure → compost / biogas</div>
        <div className="flow-label flow-label-3">produce → grading → processing → market</div>
        <div className="flow-label flow-label-4">rainwater → storage → irrigation</div>
      </div>
      <div className="system-legend"><span><i className="legend-dot green" /> resource flow</span><span><i className="legend-dot gold" /> value / money flow</span></div>
      <div className="system-footnote">Trout culture is a proposed pilot, subject to water temperature, DO, pH, and flow validation. No raw manure enters fish water. All waste streams are physically separated.</div>
      <div className="system-bottom">The innovation is not any single component. It is how the pieces work together.</div>
    </section>
  );
}

function SlideFive({ photo, onUpload, founderPhoto, onFounderUpload }) {
  const assets = [
    ["land", "Land", "7+ kanals, Mattan, Anantnag"],
    ["apple", "Orchards", "Mature apple + walnut"],
    ["water", "Water", "Canal + borewell"],
    ["leaf", "Production", "Existing vegetable garden"],
    ["pin", "Site", "31.79m × 20m complex zone mapped"],
  ];
  return (
    <section className="deck-slide paper-slide founder-slide">
      <SlideTop number={5} eyebrow="THE FOUNDER / THE BASE" title="I am not starting from zero." />
      <div className="founder-layout">
        <div className="founder-panel">
          <PhotoSlot slot="founder" label="Saadat in orchard / on the farm" photo={founderPhoto} onUpload={onFounderUpload} className="founder-photo" />
          <div className="founder-name">Saadat</div>
          <div className="founder-role">B.Tech Food Technology, IUST Kashmir<br />RISE UP Sustainable Kashmir Fellow</div>
          <div className="credential-grid">
            <div><span className="cred-icon"><Icon name="flask" size={16} /></span><strong>Food Technology</strong><small>Processing · food safety · quality · product development</small></div>
            <div><span className="cred-icon"><Icon name="chart" size={16} /></span><strong>Research + Industry</strong><small>Analytical skills · industrial exposure · evidence-based planning</small></div>
            <div><span className="cred-icon"><Icon name="leaf" size={16} /></span><strong>Permaculture + Integrated Farming</strong><small>Field learning · RISE UP fellowship · farm design</small></div>
            <div><span className="cred-icon"><Icon name="box" size={16} /></span><strong>Plan Already Built</strong><small>Research-backed plan · site survey · field visits</small></div>
          </div>
        </div>
        <div className="assets-panel">
          <div className="section-label"><span>THE EXISTING BASE</span><i /></div>
          <PhotoSlot slot="land" label="Your land / orchard / water access" photo={photo} onUpload={onUpload} className="asset-photo" />
          <div className="asset-list">
            {assets.map(([icon, title, detail]) => <div className="asset-row" key={title}><span className="asset-icon"><Icon name={icon} size={19} /></span><div><strong>{title}</strong><small>{detail}</small></div></div>)}
          </div>
          <div className="founder-quote">Most applicants have an idea. I have a site, a degree, existing infrastructure, and a validated plan.</div>
        </div>
      </div>
    </section>
  );
}

function SlideSix() {
  const levels = [
    ["ROOF", "Solar PV + rainwater collection", "roof"],
    ["LEVEL 3", "Modular hydroponic fodder", "fodder"],
    ["LEVEL 2", "Poultry · desi + broiler, separated", "poultry"],
    ["LEVEL 1", "Sheep housing · ventilated + washable", "sheep"],
    ["GROUND", "4 proposed trout raceways", "fish"],
  ];
  return (
    <section className="deck-slide paper-slide architecture-slide">
      <SlideTop number={6} eyebrow="THE BUILD / PHASE 3–4 VISION" title="Technology serves the farm — not the other way around." />
      <div className="architecture-layout">
        <div className="building-wrap">
          <div className="building-label building-label-roof"><span>ROOF</span> Solar PV + rainwater collection</div>
          <div className="building">
            <div className="building-roof"><div className="solar-panel">☼ ☼ ☼ ☼</div><div className="water-tank"><Icon name="water" size={18} /></div></div>
            {levels.slice(1).map(([label, text, type]) => <div className={`building-level level-${type}`} key={label}><span className="level-name">{label}</span><span className="level-icon"><Icon name={type === "fodder" ? "leaf" : type === "poultry" ? "chicken" : type === "sheep" ? "sheep" : "fish"} size={20} /></span><span>{text}</span></div>)}
            <div className="building-foundation"><span>water management + solids handling</span><span>compost / biogas</span></div>
          </div>
          <div className="building-side-note"><span>PHYSICAL<br />SEPARATION</span><i /></div>
          <div className="flow-ribbons"><span className="ribbon water"><i /> water</span><span className="ribbon feed"><i /> feed</span><span className="ribbon waste"><i /> waste</span><span className="ribbon energy"><i /> energy</span></div>
        </div>
        <div className="architecture-notes">
          <div className="architecture-callout"><span className="callout-index">A</span><div><strong>Low-cost</strong><small>Local stone, timber, simple steel frame</small></div></div>
          <div className="architecture-callout"><span className="callout-index">B</span><div><strong>Modular</strong><small>Build only after Phase 1 evidence</small></div></div>
          <div className="architecture-callout"><span className="callout-index">C</span><div><strong>Passive first</strong><small>Ventilation + gravity-fed where possible</small></div></div>
          <div className="architecture-callout"><span className="callout-index">D</span><div><strong>Locally serviceable</strong><small>Water testing + controls, not spectacle</small></div></div>
          <div className="architecture-sidecopy">A concept for a buildable farm complex — not a futuristic tower.</div>
        </div>
      </div>
      <div className="architecture-footer">CONCEPTUAL ARCHITECTURE · Structural, water-quality, animal-health, and regulatory validation required before construction. This is a Phase 3–4 vision, not a Phase 1 build.</div>
    </section>
  );
}

function SlideSeven() {
  const comparison = [
    ["Revenue streams", "1–2", "5–6 (phased)"],
    ["Input cost", "High (external)", "Lower (internal cycling)"],
    ["Waste value", "Zero", "Compost · fodder · biogas"],
    ["Processing margin", "Lost to middlemen", "Captured on-farm"],
    ["Scalability", "Land-dependent", "Model-dependent"],
  ];
  return (
    <section className="deck-slide paper-slide economics-slide">
      <SlideTop number={7} eyebrow="THE ECONOMIC THESIS" title="The real opportunity: more value from the same land." />
      <div className="economics-top">
        <div className="economics-flow current-flow"><div className="flow-head"><span>01</span><div><small>CURRENT MODEL</small><strong>Linear extraction</strong></div></div><div className="big-flow">Land <b>→</b> Single crop <b>→</b> Raw sale <b>→</b> <em>Value leaves farm</em></div><ul><li>One revenue stream</li><li>High purchased inputs</li><li>Waste = cost</li><li>No processing margin</li></ul></div>
        <div className="economics-arrow"><span>THESIS</span><Icon name="arrow" size={23} /></div>
        <div className="economics-flow proposed-flow"><div className="flow-head"><span>02</span><div><small>PROPOSED MODEL</small><strong>Circular capture</strong></div></div><div className="big-flow">Land <b>→</b> Multiple enterprises <b>→</b> Resource cycling <b>→</b> <em>Value addition</em></div><ul><li>Diversified income</li><li>Lower input dependence</li><li>Waste = resource</li><li>Processing margin captured on-farm</li></ul></div>
      </div>
      <div className="economic-levers"><div className="lever-intro"><span>03</span><strong>THREE<br />ECONOMIC<br />LEVERS</strong></div><div className="lever"><span>01</span><strong>More output per unit of land</strong><small>Diversification increases total production per kanal</small></div><div className="lever"><span>02</span><strong>Lower purchased-input dependence</strong><small>Internal cycling of compost, fodder, water, energy</small></div><div className="lever"><span>03</span><strong>More value captured after production</strong><small>Grading, processing, packaging, branding</small></div></div>
      <div className="competition-wrap"><div className="table-kicker">TRADITIONAL FARM <span>vs.</span> MY MODEL</div><div className="comparison-table">{comparison.map(([label, oldValue, newValue]) => <div className="comparison-row" key={label}><strong>{label}</strong><span>{oldValue}</span><span>{newValue}</span></div>)}</div><div className="assumption">HYPOTHESIS TO TEST: More output + less waste + better value capture = stronger unit economics per kanal. <b>ASSUMPTION — to be validated in Phase 1.</b></div></div>
      <Source>ICAR integrated-farming studies for the operating direction; comparative economics are a pilot hypothesis, not a measured result.</Source>
    </section>
  );
}

function SlideEight() {
  const customers = ["Local households", "Restaurants / hospitality", "Premium D2C", "Value-added products", "Farmer aggregation"];
  const criteria = ["Repeat demand", "Short delivery distance", "Reasonable price premium", "Predictable volume", "Fast feedback loop", "Low acquisition cost"];
  return (
    <section className="deck-slide paper-slide market-slide">
      <SlideTop number={8} eyebrow="THE FIRST CUSTOMER" title="Start with customers I can serve well — then expand." />
      <div className="market-ladder">
        <div className="ladder-label">MARKET LADDER <span>learn first · widen later</span></div>
        <div className="ladder-steps">{customers.map((customer, i) => <div className={`ladder-step step-${i + 1}`} key={customer}><span>0{i + 1}</span><strong>{customer}</strong><i>{i < 4 ? "→" : "↗"}</i></div>)}</div>
        <div className="ladder-product"><span>Fresh produce</span><b>→</b><span>Graded / packed</span><b>→</b><span>Processed</span><b>→</b><span>Branded</span><b>→</b><span>Aggregated</span></div>
      </div>
      <div className="market-bottom">
        <div className="criteria-panel"><div className="panel-heading"><span>01</span><strong>FIRST CUSTOMER<br />CRITERIA</strong><small>The filter before the sale</small></div><div className="criteria-list">{criteria.map((criterion) => <div key={criterion}><span><Icon name="check" size={13} /></span>{criterion}</div>)}</div><div className="first-customer"><small>FIRST CUSTOMER</small><strong>Local households + small hospitality</strong><span>Mattan / Anantnag</span></div></div>
        <div className="unit-panel"><div className="panel-heading"><span>02</span><strong>PHASE 1 UNIT<br />ECONOMICS</strong><small>Pilot assumptions, not guarantees</small></div><div className="unit-table"><div><span>Phase 1 revenue target</span><strong>₹5–10 lakh / year</strong></div><div><span>Primary sources</span><strong>Orchard · vegetables · poultry · honey</strong></div><div><span>Key cost drivers</span><strong>Feed · labour · irrigation · inputs</strong></div><div><span>Margin improvement lever</span><strong>Reduced waste + direct sales</strong></div><div><span>Timeline to first revenue</span><strong>6–12 months</strong></div></div><div className="pilot-label">PILOT ASSUMPTION · TO BE VALIDATED</div></div>
      </div>
      <div className="market-bottomline">My first customer is the customer I can learn from, not the biggest customer I can imagine.</div>
      <Source>Revenue, timeline, and mix are pilot assumptions supplied for Phase 1 planning; no current performance implied.</Source>
    </section>
  );
}

function SlideNine() {
  const ecosystem = [
    ["SKUAST-K / KVK", "Technical guidance, HADP-13 demonstrations"],
    ["J&K Agriculture Dept.", "Subsidies, MIDH, soil health"],
    ["J&K Fisheries Dept.", "Trout validation, PMMSY"],
    ["PMFME (MoFPI)", "35% processing subsidy"],
    ["StartupJK / JKEDI", "Incubation, mentorship, seed"],
    ["DIC Anantnag", "Local processing ecosystem"],
    ["Local SHGs / FPOs", "Farmer aggregation (Phase 4+)"],
  ];
  return (
    <section className="deck-slide paper-slide roadmap-slide">
      <SlideTop number={9} eyebrow="THE ROADMAP / THE ECOSYSTEM" title="Prove → Sell → Repeat → Aggregate → Scale" />
      <div className="phase-timeline">{phases.map((phase) => <div className={`phase-card ${phase.tone}`} key={phase.phase}><div className="phase-card-top"><span>{phase.phase}</span><small>{phase.years}</small></div><strong>{phase.name}</strong><p>{phase.body}</p>{phase.target && <b className="phase-target">{phase.target}</b>}</div>)}</div>
      <div className="roadmap-rule"><span>Every phase must earn the right to become the next phase.</span><i /></div>
      <div className="ecosystem"><div className="ecosystem-heading"><span>THE SUPPORTING LANDSCAPE</span><small>Fit into the institutions already building Kashmir’s food economy.</small></div><div className="ecosystem-grid">{ecosystem.map(([partner, role]) => <div className="ecosystem-row" key={partner}><strong>{partner}</strong><span>{role}</span></div>)}</div></div>
    </section>
  );
}

function SlideTen() {
  const validation = [
    ["2026–27", "Soil/water tests · Crop trials · Poultry mortality", "First revenue · Customer feedback · Cost tracking", "Labour · Waste · Water use"],
    ["2027–28", "Trout water validation · Fodder yield · Greenhouse performance", "Repeat customers · Margin per enterprise", "Energy · Feed efficiency"],
    ["2028–29", "Processing trials · Shelf life · Quality testing", "Processing revenue · Brand recognition", "Processing costs · Supply chain"],
    ["2029–30", "Farmer pilot data · Aggregation logistics", "Network revenue · Shared processing", "Replication model"],
  ];
  const impact = [
    ["Reduced waste burning", "Composting crop residues", "ICAR integrated farming studies"],
    ["Lower chemical inputs", "Organic compost replaces synthetic fertilizer", "HADP-13 circular farming model"],
    ["Water efficiency", "Rainwater harvesting + drip irrigation", "NITI Aayog J&K water recommendations"],
    ["Carbon sequestration", "Orchard preservation + soil organic matter", "Permaculture research"],
    ["Biodiversity", "Pollinator habitat + mixed cropping", "ICAR-CITH Srinagar"],
  ];
  return (
    <section className="deck-slide paper-slide close-slide">
      <SlideTop number={10} eyebrow="THE ASK / THE MEASUREMENT PLAN" title="Build one farm that works. Then make the model useful to many." />
      <div className="validation-section"><div className="close-section-heading"><span>01</span><strong>VALIDATION MILESTONES</strong><small>Every assumption gets a metric.</small></div><div className="validation-table"><div className="validation-head"><span>YEAR</span><span>TECHNICAL</span><span>COMMERCIAL</span><span>OPERATIONAL</span></div>{validation.map((row) => <div className="validation-row" key={row[0]}><strong>{row[0]}</strong><span>{row[1]}</span><span>{row[2]}</span><span>{row[3]}</span></div>)}</div></div>
      <div className="impact-section"><div className="close-section-heading"><span>02</span><strong>CLIMATE + ENVIRONMENTAL IMPACT</strong><small>Directional, evidence-based — not overclaimed.</small></div><div className="impact-table">{impact.map((row) => <div className="impact-row" key={row[0]}><strong>{row[0]}</strong><span>{row[1]}</span><small>{row[2]}</small></div>)}</div><div className="impact-foot">Directional impact estimates. Formal lifecycle assessment to be conducted in Phase 2.</div></div>
      <div className="mission-block"><div className="mission-label">03 / MISSION</div><blockquote>“I don’t need to prove the whole vision today.<br /><em>I need to prove the first piece.</em>”</blockquote><div className="vision-line"><span>2030 vision</span><strong>₹5 crore annual revenue · ~5,000-family livelihood impact</strong><small>LONG-TERM VISION — directional targets, not current performance</small></div></div>
      <div className="final-tagline">Innovate today. Prove it. Scale tomorrow.</div>
    </section>
  );
}

function Deck() {
  const [current, setCurrent] = useState(0);
  const [showNotes, setShowNotes] = useState(false);
  const [photos, setPhotos] = useState({});
  const [isFullscreen, setIsFullscreen] = useState(false);
  const stageRef = useRef(null);

  const uploadPhoto = (slot, event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setPhotos((previous) => ({ ...previous, [slot]: reader.result }));
    reader.readAsDataURL(file);
    event.target.value = "";
  };

  const slides = useMemo(() => [
    <SlideOne photo={photos.cover} onUpload={uploadPhoto} />,
    <SlideTwo photo={photos.problem} onUpload={uploadPhoto} />,
    <SlideThree />,
    <SlideFour />,
    <SlideFive photo={photos.land} founderPhoto={photos.founder} onUpload={uploadPhoto} onFounderUpload={uploadPhoto} />,
    <SlideSix />,
    <SlideSeven />,
    <SlideEight />,
    <SlideNine />,
    <SlideTen />,
  ], [photos]);

  const goTo = useCallback(
    (index) => setCurrent(Math.min(Math.max(index, 0), slides.length - 1)),
    [slides.length]
  );

  useEffect(() => {
    const onKey = (event) => {
      if (["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
      if (event.key === "ArrowRight" || event.key === "PageDown" || event.key === " ") {
        event.preventDefault();
        goTo(current + 1);
      }
      if (event.key === "ArrowLeft" || event.key === "PageUp") {
        event.preventDefault();
        goTo(current - 1);
      }
      if (event.key.toLowerCase() === "n") setShowNotes((value) => !value);
      if (event.key.toLowerCase() === "f") toggleFullscreen();
      if (event.key === "Home") goTo(0);
      if (event.key === "End") goTo(slides.length - 1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [current, goTo, slides.length]);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      stageRef.current?.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  useEffect(() => {
    const onFullscreen = () => setIsFullscreen(Boolean(document.fullscreenElement));
    document.addEventListener("fullscreenchange", onFullscreen);
    return () => document.removeEventListener("fullscreenchange", onFullscreen);
  }, []);

  return (
    <main className="deck-app">
      <div className="deck-utility-bar">
        <div className="deck-brand"><span className="brand-dot" /> SAADAT / FIELD NOTE <b>01—10</b></div>
        <div className="deck-utility-actions"><button type="button" onClick={() => setShowNotes((value) => !value)} className={showNotes ? "active" : ""}><span className="utility-icon">☰</span> Speaker notes <kbd>N</kbd></button><button type="button" onClick={toggleFullscreen}><span className="utility-icon">⛶</span> {isFullscreen ? "Exit" : "Present"} <kbd>F</kbd></button><button type="button" onClick={() => window.print()}><span className="utility-icon">↗</span> Print / PDF</button></div>
      </div>
      <div className="deck-workspace">
        <div className="deck-stage" ref={stageRef} aria-label={`Slide ${current + 1} of ${slides.length}`}>
          <div className="slide-progress"><span style={{ width: `${((current + 1) / slides.length) * 100}%` }} /></div>
          <div key={current} className="slide-transition">{slides[current]}</div>
          <button type="button" className="stage-nav stage-prev" onClick={() => goTo(current - 1)} disabled={current === 0} aria-label="Previous slide">‹</button>
          <button type="button" className="stage-nav stage-next" onClick={() => goTo(current + 1)} disabled={current === slides.length - 1} aria-label="Next slide">›</button>
        </div>
        <div className="deck-controls">
          <button type="button" className="control-arrow" onClick={() => goTo(current - 1)} disabled={current === 0}>←</button>
          <div className="slide-dots" aria-label="Slide navigation">{slides.map((_, index) => <button type="button" key={index} className={index === current ? "selected" : ""} onClick={() => goTo(index)} aria-label={`Go to slide ${index + 1}`}><span>{String(index + 1).padStart(2, "0")}</span></button>)}</div>
          <button type="button" className="control-arrow" onClick={() => goTo(current + 1)} disabled={current === slides.length - 1}>→</button>
          <div className="control-count"><strong>{String(current + 1).padStart(2, "0")}</strong><span>/ 10</span></div>
        </div>
        <div className="deck-hint">Use ← → to navigate <span>·</span> <strong>real photos stay local to this preview</strong></div>
      </div>
      <div className="print-deck" aria-hidden="true">
        {slides.map((slide, index) => <div className="print-slide" key={`print-${index}`}>{slide}</div>)}
      </div>
      {showNotes && <aside className="notes-panel"><div className="notes-head"><div><span>SLIDE {String(current + 1).padStart(2, "0")}</span><strong>Speaker notes</strong></div><button type="button" onClick={() => setShowNotes(false)} aria-label="Close speaker notes">×</button></div><p>{notes[current]}</p><div className="notes-footer">Approx. {current === 0 ? "60" : current === 1 || current === 2 || current === 3 || current === 6 || current === 7 || current === 8 || current === 9 ? "90" : "75"} seconds · {current === 9 ? "closing ask" : "presentation narrative"}</div></aside>}
    </main>
  );
}

export default Deck;
