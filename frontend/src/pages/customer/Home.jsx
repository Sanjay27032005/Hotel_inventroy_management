import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui";

const HERO_SLIDES = [
  {
    image: "https://images.unsplash.com/photo-1519225421980-715cb0215aed?q=80&w=1200&auto=format&fit=crop",
    title: "WELCOME TO CORESTONE GRAND",
    subtitle: "Experience unrivaled hospitality, all under one roof.",
    ctaText: "ORDER NOW",
    ctaLink: "/book-a-stay"
  },
  {
    image: "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?q=80&w=1200&auto=format&fit=crop",
    title: "LUXURIOUS ACCOMMODATIONS",
    subtitle: "Retreat into absolute comfort with our premium suites.",
    ctaText: "EXPLORE ROOMS",
    ctaLink: "/services#accommodation"
  },
  {
    image: "https://images.unsplash.com/photo-1519046904884-53103b34b206?q=80&w=1200&auto=format&fit=crop",
    title: "FINE DINING EXPERIENCE",
    subtitle: "Savor exquisite global flavors curated by master chefs.",
    ctaText: "VIEW MENU",
    ctaLink: "/dining"
  }
];

const TABBED_SERVICES = {
  "Accommodation": [
    { name: "Single Suite", price: "₹5000 / Night" },
    { name: "Couple Suite", price: "₹8000 / Night" },
    { name: "Family Suite", price: "₹12000 / Night" }
  ],
  "Fine Dining": [
    { name: "Continental Breakfast", price: "₹1200" },
    { name: "Signature Steak", price: "₹3500" },
    { name: "Chef's Tasting Menu", price: "₹5500" }
  ],
  "Spa & Wellness": [
    { name: "Traditional Massage", price: "₹2500" },
    { name: "Hot Stone Therapy", price: "₹4000" },
    { name: "Reflexology", price: "₹2000" }
  ],
  "Events": [
    { name: "Intimate Hall", price: "₹25000 / Day" },
    { name: "Grand Ballroom", price: "₹75000 / Day" }
  ]
};

export default function Home() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [activeTab, setActiveTab] = useState("Accommodation");

  // Auto-play carousel
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % HERO_SLIDES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const nextSlide = () => setCurrentSlide((p) => (p + 1) % HERO_SLIDES.length);
  const prevSlide = () => setCurrentSlide((p) => (p === 0 ? HERO_SLIDES.length - 1 : p - 1));

  return (
    <div className="bg-ink-900 text-linen-50 font-sans">
      
      {/* 1. Hero Carousel */}
      <section className="relative h-[85vh] w-full overflow-hidden flex items-center justify-center bg-black">
        {HERO_SLIDES.map((slide, index) => (
          <div 
            key={index} 
            className={`absolute inset-0 transition-opacity duration-1000 ${index === currentSlide ? "opacity-100 z-10 pointer-events-auto" : "opacity-0 z-0 pointer-events-none"}`}
          >
            <div className="absolute inset-0 overflow-hidden">
               <img 
                 src={slide.image} 
                 alt={slide.title}
                 className={`h-full w-full object-cover opacity-90 ${index === currentSlide ? 'animate-[kenburns_20s_ease-in-out_infinite_alternate]' : ''}`}
               />
               <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-ink-900/20 to-transparent"></div>
               <div className="absolute inset-0 bg-black/20"></div>
            </div>
            <div className="relative z-20 flex h-full flex-col items-center justify-center text-center px-4">
              <h1 className="font-display text-4xl sm:text-6xl md:text-7xl font-bold tracking-wider text-white uppercase drop-shadow-2xl">
                {slide.title.split(' ').map((word, i) => word === "ZAITOON" || word === "CORESTONE" || word === "RESTAURANT" || word === "GRAND" ? <span key={i} className="text-brass-400">{word} </span> : <span key={i}>{word} </span>)}
              </h1>
              <p className="mt-4 max-w-2xl text-lg sm:text-xl text-linen-100 drop-shadow-md">
                {slide.subtitle}
              </p>
              <Button variant="brass" size="lg" as={Link} to={slide.ctaLink} className="mt-8 px-10 py-4 text-sm font-bold uppercase tracking-widest shadow-xl">
                {slide.ctaText}
                <svg className="ml-3 h-4 w-4 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
              </Button>
            </div>
          </div>
        ))}
        
        {/* Carousel Controls */}
        <button onClick={prevSlide} className="absolute left-4 top-1/2 -translate-y-1/2 z-30 p-3 rounded-full bg-black/20 text-white hover:bg-brass-500 transition-colors backdrop-blur-sm border border-white/10 hidden md:block">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
        </button>
        <button onClick={nextSlide} className="absolute right-4 top-1/2 -translate-y-1/2 z-30 p-3 rounded-full bg-black/20 text-white hover:bg-brass-500 transition-colors backdrop-blur-sm border border-white/10 hidden md:block">
           <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
        </button>

        {/* Carousel Indicators */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-30 flex space-x-2">
          {HERO_SLIDES.map((_, i) => (
             <button 
               key={i}
               onClick={() => setCurrentSlide(i)}
               className={`h-2 w-8 rounded-full transition-colors ${i === currentSlide ? 'bg-brass-400' : 'bg-white/30 hover:bg-white/50'}`}
             />
          ))}
        </div>
      </section>

      {/* 2. About Us Section (Split Layout) */}
      <section className="mx-auto max-w-7xl px-6 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="font-display text-4xl sm:text-5xl font-bold uppercase text-white">
              About <span className="text-brass-500">Us</span>
            </h2>
            <p className="mt-6 text-lg text-linen-200/80 leading-relaxed">
              CoreStone Grand — the premier luxury destination for authentic hospitality, exquisite fine dining, and ultimate relaxation. Whether you're indulging in our slow-cooked signature dishes, unwinding at our world-class spa, or celebrating in our grand halls, we guarantee a warm, unforgettable experience.
            </p>
            <Button variant="outline" as={Link} to="/services" className="mt-8 border-brass-500 text-brass-400 hover:bg-brass-500 hover:text-ink-900 transition-colors">
              Discover More
            </Button>
          </div>
          <div className="relative">
             <div className="aspect-[4/3] overflow-hidden rounded-2xl shadow-2xl">
               <img 
                 src="https://images.unsplash.com/photo-1519046904884-53103b34b206?q=80&w=1200&auto=format&fit=crop" 
                 alt="About CoreStone" 
                 className="h-full w-full object-cover transition-transform duration-700 hover:scale-105"
               />
             </div>
             {/* Decorative element */}
             <div className="absolute -bottom-6 -left-6 w-32 h-32 border-b-4 border-l-4 border-brass-500 rounded-bl-3xl -z-10"></div>
          </div>
        </div>
      </section>

      {/* 3. Our Menu / Services Tabs */}
      <section className="bg-[#162723] py-20 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 text-center">
           <h2 className="font-display text-4xl sm:text-5xl font-bold uppercase text-white mb-12">
             Our <span className="text-brass-500">Menu</span>
           </h2>
           
           {/* Tabs Header */}
           <div className="flex flex-wrap justify-center gap-2 mb-12 border-b border-white/10 pb-4">
             {Object.keys(TABBED_SERVICES).map(tab => (
               <button
                 key={tab}
                 onClick={() => setActiveTab(tab)}
                 className={`px-6 py-3 font-semibold uppercase tracking-wider text-sm transition-all duration-300 rounded-t-lg ${activeTab === tab ? 'bg-brass-500 text-ink-900 shadow-[0_-4px_15px_rgba(198,161,91,0.3)]' : 'text-linen-200/60 hover:text-white hover:bg-white/5'}`}
               >
                 {tab}
               </button>
             ))}
           </div>

           {/* Tabs Content */}
           <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 text-left">
             {TABBED_SERVICES[activeTab].map((item, idx) => (
               <div key={idx} className="bg-ink-900 border border-white/10 rounded-xl p-6 transition-transform hover:-translate-y-2 hover:border-brass-500/50 hover:shadow-xl hover:shadow-brass-900/20 group">
                 <div className="flex justify-between items-start">
                   <h3 className="font-display text-xl text-white group-hover:text-brass-400 transition-colors">{item.name}</h3>
                 </div>
                 <p className="mt-4 text-lg font-bold text-brass-500">{item.price}</p>
                 <Link to="/services" className="inline-flex mt-6 items-center text-sm font-medium text-linen-200/50 group-hover:text-brass-400 transition-colors">
                   View Details <span className="ml-1">→</span>
                 </Link>
               </div>
             ))}
           </div>
           
           <div className="mt-16">
             <Button variant="brass" as={Link} to="/services" className="px-12 py-4">
               VIEW FULL OFFERINGS
             </Button>
           </div>
        </div>
      </section>

      {/* Membership Call to Action */}
      <section className="relative overflow-hidden py-24 text-center">
        <div className="absolute inset-0 z-0 overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1560624052-449f5ddf0c31?q=80&w=1200&auto=format&fit=crop"
            alt="Luxury Lifestyle"
            className="h-full w-full object-cover opacity-80 animate-[kenburns_25s_ease-in-out_infinite_alternate]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-ink-900/60 to-ink-900/40"></div>
        </div>
        <div className="relative z-10 mx-auto max-w-3xl px-6">
          <h2 className="font-display text-4xl text-brass-400 sm:text-5xl uppercase font-bold">Elevate Your Lifestyle</h2>
          <p className="mt-6 text-lg text-linen-200/80 leading-relaxed">
            Join the CoreStone Privilege Club. Our exclusive tiers offer unprecedented access and exceptional value across our entire portfolio.
          </p>
          <div className="mt-10">
            <Button variant="brass" size="lg" as={Link} to="/membership" className="px-10 py-4 shadow-lg shadow-brass-500/20 uppercase font-bold tracking-widest">
              View Privileges
            </Button>
          </div>
        </div>
      </section>

    </div>
  );
}
