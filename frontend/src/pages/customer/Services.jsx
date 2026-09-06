import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  roomApi, restaurantApi, partyHallApi, poolApi, spaApi, clubApi, laundryApi,
} from "../../api/endpoints";
import { Button, Spinner } from "../../components/ui";

function ServiceSection({ id, title, description, image, children }) {
  return (
    <section id={id} className="scroll-mt-24 py-16 border-b border-ink-700/10 last:border-0">
      <div className="grid gap-10 lg:grid-cols-[1fr_2fr] lg:gap-16">
        <div>
          <div className="sticky top-24">
            {image && (
              <div className="mb-6 overflow-hidden rounded-xl bg-linen-200 aspect-[4/3] relative group bg-black">
                {image.endsWith('.mp4') ? (
                   <video src={image} autoPlay loop muted playsInline className="h-full w-full object-cover opacity-90 transition-transform duration-[10000ms] group-hover:scale-110" />
                ) : (
                   <img src={image} alt={title} className="h-full w-full object-cover transition-transform duration-[10000ms] group-hover:scale-125 animate-[kenburns_15s_ease-in-out_infinite_alternate]" />
                )}
              </div>
            )}
            <h2 className="font-display text-4xl text-ink-900">{title}</h2>
            <p className="mt-4 text-lg text-ink-700/80 leading-relaxed">{description}</p>
          </div>
        </div>
        <div>
          {children}
        </div>
      </div>
    </section>
  );
}

function InfoGrid({ items, render }) {
  if (!items.length) return (
    <div className="flex h-48 items-center justify-center rounded-xl border border-dashed border-ink-700/20 bg-ink-50/50">
      <p className="text-sm text-ink-700/60">Details and pricing being updated. Please check back later.</p>
    </div>
  );
  return <div className="grid gap-4 sm:grid-cols-2">{items.map(render)}</div>;
}

const MOCK_ROOMS = [
  { id: 1, name: "Presidential Suite", customer_category: "VIP", daily_rate: "55000", hourly_rate: "5000" },
  { id: 2, name: "Luxury Family Suite", customer_category: "Family", daily_rate: "25000", hourly_rate: "2500" },
  { id: 3, name: "Couples Retreat", customer_category: "Couples", daily_rate: "18000", hourly_rate: "2000" },
  { id: 4, name: "Executive Single", customer_category: "Solo", daily_rate: "12000", hourly_rate: "1500" }
];

const MOCK_MENU = [
  { id: 1, name: "Truffle Lobster Risotto", price: "4500" },
  { id: 2, name: "Wagyu Beef Steak", price: "6500" },
  { id: 3, name: "Saffron Infused Biryani", price: "2200" },
  { id: 4, name: "Gold Leaf Chocolate Tart", price: "1800" },
];

const MOCK_HALLS = [
  { id: 1, name: "The Crystal Ballroom", capacity: "500", daily_rate: "250000", hourly_rate: "25000" },
  { id: 2, name: "Imperial Conference Room", capacity: "50", daily_rate: "50000", hourly_rate: "5000" },
];

const MOCK_SPA = [
  { id: 1, name: "24k Gold Facial", service_price: "8000" },
  { id: 2, name: "Deep Tissue Massage (90 Min)", service_price: "5500" },
  { id: 3, name: "Aromatherapy Journey", service_price: "4500" },
];

const MOCK_POOL = [
  { id: 1, package_type: "Monthly Pass", customer_type: "Individual", price: "12000" },
  { id: 2, package_type: "Day Pass with Cabana", customer_type: "Family", price: "8000" },
];

const MOCK_CLUB = [
  { id: 1, name: "Aged Single Malt (Peg)", unit_price: "2500" },
  { id: 2, name: "Signature Caviar Platter", unit_price: "12000" },
  { id: 3, name: "Artisanal Cheese Board", unit_price: "4500" }
];

const MOCK_LAUNDRY = [
  { id: 1, cloth_type: "Two-Piece Suit (Dry Clean)", unit_price: "1200" },
  { id: 2, cloth_type: "Evening Gown", unit_price: "2500" },
];

export default function Services() {
  const [data, setData] = useState({
    roomTypes: MOCK_ROOMS, menu: MOCK_MENU, halls: MOCK_HALLS, poolPrices: MOCK_POOL, spaServices: MOCK_SPA, clubFood: MOCK_CLUB, laundryPrices: MOCK_LAUNDRY,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      roomApi.types().catch(() => ({ data: [] })), 
      restaurantApi.menu().catch(() => ({ data: [] })), 
      partyHallApi.halls().catch(() => ({ data: [] })), 
      poolApi.prices().catch(() => ({ data: [] })),
      spaApi.services().catch(() => ({ data: [] })), 
      clubApi.foodItems().catch(() => ({ data: [] })), 
      laundryApi.prices().catch(() => ({ data: [] })),
    ])
      .then(([roomTypes, menu, halls, poolPrices, spaServices, clubFood, laundryPrices]) => {
        setData({
          roomTypes: roomTypes.data.length ? roomTypes.data : MOCK_ROOMS, 
          menu: menu.data.length ? menu.data : MOCK_MENU, 
          halls: halls.data.length ? halls.data : MOCK_HALLS, 
          poolPrices: poolPrices.data.length ? poolPrices.data : MOCK_POOL,
          spaServices: spaServices.data.length ? spaServices.data : MOCK_SPA, 
          clubFood: clubFood.data.length ? clubFood.data : MOCK_CLUB, 
          laundryPrices: laundryPrices.data.length ? laundryPrices.data : MOCK_LAUNDRY,
        });
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center space-y-4">
        <Spinner className="h-8 w-8 text-brass-500" />
        <p className="font-display text-lg text-ink-900 animate-pulse">Curating services...</p>
      </div>
    );
  }

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-ink-900 text-linen-50">
        <div className="absolute inset-0 z-0 overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1499856871958-5b9627545d1a?q=80&w=1200&auto=format&fit=crop"
            alt="Services"
            className="h-full w-full object-cover opacity-90 animate-[kenburns_25s_ease-in-out_infinite_alternate]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-black/10"></div>
        </div>
        <div className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:py-32 text-center">
          <p className="text-sm font-medium tracking-widest text-brass-400 uppercase">CoreStone Grand Experiences</p>
          <h1 className="mt-4 font-display text-5xl font-light text-linen-50 sm:text-6xl md:text-7xl">
            Our Signature <span className="font-medium">Services</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-linen-200/80 leading-relaxed">
            Seven bespoke services tailored to perfection. Experience uncompromising luxury and comfort, all united under one seamless bill at check-out.
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-6 py-12">
        <ServiceSection
          id="accommodation"
          title="Accommodation"
          description="Retreat into luxury. Our exquisitely designed suites cater to solo travelers, couples, and families. Flexible pricing allows you to book by the hour, day, week, or month."
          image="https://images.unsplash.com/photo-1439066615861-d1af74d74000?q=80&w=1200&auto=format&fit=crop"
        >
          <InfoGrid
            items={data.roomTypes}
            render={(rt) => (
              <div key={rt.id} className="group flex flex-col justify-between rounded-xl border border-ink-700/10 bg-white p-6 shadow-sm transition-all hover:border-brass-300 hover:shadow-md">
                <div>
                  <h3 className="font-display text-xl text-ink-900 group-hover:text-brass-700 transition-colors">{rt.name}</h3>
                  <p className="mt-1 inline-block rounded-full bg-brass-50 px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide text-brass-700">{rt.customer_category}</p>
                </div>
                <div className="mt-6 pt-4 border-t border-ink-700/5">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-xs text-ink-700/60 uppercase">Nightly</p>
                      <p className="font-display text-lg text-ink-900">₹{rt.daily_rate}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-ink-700/60 uppercase">Hourly</p>
                      <p className="font-display text-lg text-ink-900">₹{rt.hourly_rate}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          />
        </ServiceSection>

        <ServiceSection 
          id="restaurant" 
          title="Fine Dining" 
          description="Savor global flavors and local delicacies. Our master chefs prepare extraordinary dishes from breakfast through dinner, served with impeccable hospitality."
          image="https://images.unsplash.com/photo-1518684079-3c830dcef090?q=80&w=1200&auto=format&fit=crop"
        >
          <InfoGrid
            items={data.menu.slice(0, 8)}
            render={(item) => (
              <div key={item.id} className="flex items-center justify-between rounded-xl border border-ink-700/10 bg-white p-5 shadow-sm transition-all hover:border-brass-300 hover:shadow-md">
                <p className="font-medium text-ink-900 text-lg">{item.name}</p>
                <p className="font-display text-lg text-brass-700 bg-brass-50 px-3 py-1 rounded-full">₹{item.price}</p>
              </div>
            )}
          />
          {data.menu.length > 8 && (
             <div className="mt-4 text-center">
                <p className="text-sm text-ink-700/60 italic">And many more culinary delights await...</p>
             </div>
          )}
        </ServiceSection>

        <ServiceSection 
          id="party-hall" 
          title="Grand Venues" 
          description="Host unforgettable events. Whether it's an intimate birthday, a grand wedding, or a high-stakes corporate conference, our halls are equipped for perfection."
          image="https://images.unsplash.com/photo-1469334031218-e382a71b716b?q=80&w=1200&auto=format&fit=crop"
        >
          <InfoGrid
            items={data.halls}
            render={(hall) => (
              <div key={hall.id} className="group flex flex-col justify-between rounded-xl border border-ink-700/10 bg-white p-6 shadow-sm transition-all hover:border-brass-300 hover:shadow-md">
                <div>
                  <h3 className="font-display text-xl text-ink-900 group-hover:text-brass-700 transition-colors">{hall.name}</h3>
                  <div className="mt-2 flex items-center text-sm text-ink-700/70">
                    <svg className="mr-1.5 h-4 w-4 text-brass-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                    Up to {hall.capacity} guests
                  </div>
                </div>
                <div className="mt-6 pt-4 border-t border-ink-700/5">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-xs text-ink-700/60 uppercase">Daily</p>
                      <p className="font-display text-lg text-ink-900">₹{hall.daily_rate}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-ink-700/60 uppercase">Hourly</p>
                      <p className="font-display text-lg text-ink-900">₹{hall.hourly_rate}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          />
        </ServiceSection>

        <ServiceSection 
          id="spa" 
          title="Spa & Wellness" 
          description="Find your zen. Indulge in traditional treatments, authentic Thai massages, hot stone therapy, and reflexology led by our expert therapists."
          image="https://images.unsplash.com/photo-1549294413-26f195200c16?q=80&w=1200&auto=format&fit=crop"
        >
          <InfoGrid
            items={data.spaServices}
            render={(svc) => (
              <div key={svc.id} className="flex items-center justify-between rounded-xl border border-ink-700/10 bg-white p-5 shadow-sm transition-all hover:border-brass-300 hover:shadow-md">
                <p className="font-medium text-ink-900 text-lg">{svc.name}</p>
                <p className="font-display text-lg text-brass-700 bg-brass-50 px-3 py-1 rounded-full">₹{svc.service_price}</p>
              </div>
            )}
          />
        </ServiceSection>

        <ServiceSection 
          id="pool" 
          title="Aquatic Center" 
          description="Dive into tranquility. Enjoy our pristine pools with hourly, monthly, and specialized trainer-led packages for individuals, couples, and children."
          image="https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=1200&auto=format&fit=crop"
        >
          <InfoGrid
            items={data.poolPrices}
            render={(p) => (
              <div key={p.id} className="group rounded-xl border border-ink-700/10 bg-white p-5 shadow-sm transition-all hover:border-brass-300 hover:shadow-md">
                <p className="font-medium capitalize text-ink-900 text-lg group-hover:text-brass-700">{p.package_type}</p>
                <p className="text-sm text-ink-700/60 capitalize mb-4">{p.customer_type}</p>
                <div className="pt-3 border-t border-ink-700/5 flex justify-between items-center">
                    <span className="text-xs uppercase font-medium text-ink-700/50">Rate</span>
                    <p className="font-display text-lg text-brass-700">₹{p.price}</p>
                </div>
              </div>
            )}
          />
        </ServiceSection>

        <ServiceSection 
          id="club" 
          title="Exclusive Club & Bar" 
          description="Unwind in style. Experience premium evening service, handcrafted cocktails, artisanal food, and live entertainment in our exclusive lounge."
          image="https://images.unsplash.com/photo-1514282401047-d79a71a590e8?q=80&w=1200&auto=format&fit=crop" 
        >
          {/* Note: Unsplash image for bar/club */}
          <InfoGrid
            items={data.clubFood}
            render={(item) => (
              <div key={item.id} className="flex items-center justify-between rounded-xl border border-ink-700/10 bg-white p-5 shadow-sm transition-all hover:border-brass-300 hover:shadow-md">
                <p className="font-medium text-ink-900 text-lg">{item.name}</p>
                <p className="font-display text-lg text-brass-700 bg-brass-50 px-3 py-1 rounded-full">₹{item.unit_price}</p>
              </div>
            )}
          />
        </ServiceSection>

        <ServiceSection 
          id="laundry" 
          title="Valet Laundry" 
          description="Impeccable garment care. Choose from piece-based or weight-based pricing, with transparent tracking from pickup to delivery directly to your suite."
          image="https://images.unsplash.com/photo-1564501049412-61c2a3083791?q=80&w=1200&auto=format&fit=crop"
        >
          <InfoGrid
            items={data.laundryPrices}
            render={(item) => (
              <div key={item.id} className="flex items-center justify-between rounded-xl border border-ink-700/10 bg-white p-5 shadow-sm transition-all hover:border-brass-300 hover:shadow-md">
                <p className="font-medium text-ink-900 text-lg">{item.cloth_type}</p>
                <p className="font-display text-lg text-brass-700 bg-brass-50 px-3 py-1 rounded-full">₹{item.unit_price}</p>
              </div>
            )}
          />
        </ServiceSection>

        <div className="relative mt-16 overflow-hidden rounded-2xl bg-ink-900 px-6 py-16 text-center shadow-2xl">
           <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 animate-[shimmer_3s_infinite_linear]"></div>
           <div className="relative z-10">
              <h2 className="font-display text-3xl text-linen-50 sm:text-4xl">Ready to curate your experience?</h2>
              <p className="mt-4 text-linen-200/80 max-w-xl mx-auto text-lg">Build a bespoke itinerary combining any of our premium services seamlessly.</p>
              <Button variant="brass" size="lg" as={Link} to="/book-a-stay" className="mt-8 px-10 shadow-lg shadow-brass-500/20">
                Design Your Stay
              </Button>
           </div>
        </div>
      </div>
    </div>
  );
}
