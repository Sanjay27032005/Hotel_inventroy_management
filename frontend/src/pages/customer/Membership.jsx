import { useEffect, useState } from "react";
import { membershipApi } from "../../api/endpoints";
import { Spinner, Button } from "../../components/ui";
import { Link } from "react-router-dom";

// Helper for premium tier colors based on plan name
const getTierStyles = (name) => {
  const lowerName = name.toLowerCase();
  if (lowerName.includes("platinum")) {
    return "bg-gradient-to-br from-ink-800 via-ink-900 to-ink-950 text-white border-ink-700 shadow-2xl shadow-brass-900/20 ring-1 ring-white/10 group overflow-hidden";
  }
  if (lowerName.includes("gold")) {
    return "bg-gradient-to-br from-[#fdfbf7] to-[#f4ead5] border-brass-300 shadow-xl shadow-brass-900/10 group overflow-hidden";
  }
  return "bg-white border-ink-700/10 shadow-lg shadow-ink-900/5 group overflow-hidden"; // Silver/Default
};

const getBadgeStyles = (name) => {
  const lowerName = name.toLowerCase();
  if (lowerName.includes("platinum")) {
    return "bg-white/10 text-white border-white/20";
  }
  if (lowerName.includes("gold")) {
    return "bg-brass-100 text-brass-800 border-brass-200";
  }
  return "bg-ink-50 text-ink-700 border-ink-200";
};

const MOCK_PLANS = [
  {
    id: 1,
    name: "Silver Tier",
    discount_percentage: 10,
    fee: 5000,
    duration_months: 12,
    benefits: "Priority check-in, Late check-out upon request, Complimentary high-speed Wi-Fi"
  },
  {
    id: 2,
    name: "Gold Tier",
    discount_percentage: 15,
    fee: 15000,
    duration_months: 12,
    benefits: "All Silver benefits, Complimentary breakfast, Access to Executive Lounge, Room upgrades (subject to availability)"
  },
  {
    id: 3,
    name: "Platinum Tier",
    discount_percentage: 25,
    fee: 35000,
    duration_months: 12,
    benefits: "All Gold benefits, Dedicated butler service, Complimentary airport transfers, Unlimited access to Aquatic Center and Spa"
  }
];

export default function Membership() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    membershipApi
      .plans()
      .then((res) => {
        setPlans(res.data?.length > 0 ? res.data : MOCK_PLANS);
      })
      .catch(() => {
        setPlans(MOCK_PLANS);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-ink-900 text-linen-50">
        <div className="absolute inset-0 z-0 overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1540555700478-4be289fbecef?q=80&w=1200&auto=format&fit=crop"
            alt="Membership"
            className="h-full w-full object-cover opacity-90 animate-[kenburns_20s_ease-in-out_infinite_alternate]"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-ink-900/40 via-transparent to-ink-900"></div>
          <div className="absolute inset-0 bg-black/10"></div>
        </div>
        <div className="relative z-10 mx-auto max-w-4xl px-6 py-24 text-center lg:py-32">
          <span className="mb-4 inline-block rounded-full border border-brass-500/30 bg-brass-500/10 px-3 py-1 text-xs tracking-widest text-brass-400 uppercase backdrop-blur-sm">
            CoreStone Privilege Club
          </span>
          <h1 className="font-display text-5xl font-bold text-white sm:text-6xl drop-shadow-2xl">
            Membership <span className="text-brass-400">Excellence</span>
          </h1>
          <p className="mt-6 text-lg text-white font-medium drop-shadow-lg leading-relaxed max-w-2xl mx-auto">
            Elevate your lifestyle with our exclusive membership tiers. Enjoy unparalleled privileges, priority bookings, and automatic discounts across our entire portfolio of premium services.
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-6 py-20">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="font-display text-3xl text-ink-900">Choose Your Privilege Level</h2>
          <p className="mt-4 text-ink-700/70">
            Enroll at the front desk or through your account. Your benefits apply instantly to rooms, dining, spa, pool, and club access.
          </p>
        </div>

        {loading ? (
          <div className="mt-16 flex flex-col items-center justify-center space-y-4">
             <Spinner className="h-8 w-8 text-brass-500" />
             <p className="text-ink-700/60 animate-pulse">Loading privileges...</p>
          </div>
        ) : (
          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3 items-center">
            {plans.map((plan) => {
              const isPlatinum = plan.name.toLowerCase().includes("platinum");
              return (
                <div 
                  key={plan.id} 
                  className={`relative flex flex-col rounded-2xl border p-8 transition-all duration-500 hover:-translate-y-3 hover:shadow-2xl ${getTierStyles(plan.name)} ${isPlatinum ? 'lg:scale-105 z-10 py-12' : ''}`}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite]"></div>
                  {isPlatinum && (
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-brass-400 via-brass-300 to-brass-500 px-4 py-1 text-xs font-bold tracking-widest text-ink-900 uppercase shadow-lg shadow-brass-500/50 animate-pulse">
                      Most Exclusive
                    </div>
                  )}
                  <div className="flex justify-between items-start">
                    <p className="font-display text-3xl font-medium">{plan.name}</p>
                    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold tracking-wide uppercase ${getBadgeStyles(plan.name)}`}>
                      {plan.discount_percentage}% OFF
                    </span>
                  </div>
                  
                  <div className="mt-6">
                    <p className={`text-4xl font-light ${isPlatinum ? 'text-white' : 'text-ink-900'}`}>
                      ₹{plan.fee}
                    </p>
                    <p className={`mt-1 text-sm ${isPlatinum ? 'text-white/60' : 'text-ink-700/60'}`}>
                      Valid for {plan.duration_months} months
                    </p>
                  </div>

                  <div className={`mt-8 flex-1 space-y-4 text-sm ${isPlatinum ? 'text-white/80' : 'text-ink-700/80'}`}>
                    <div className="flex items-start">
                      <svg className={`mr-3 h-5 w-5 shrink-0 ${isPlatinum ? 'text-brass-400' : 'text-brass-600'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                      <span>{plan.discount_percentage}% discount on eligible services</span>
                    </div>
                    {plan.benefits && plan.benefits.split(',').map((benefit, i) => (
                      <div key={i} className="flex items-start">
                        <svg className={`mr-3 h-5 w-5 shrink-0 ${isPlatinum ? 'text-brass-400' : 'text-brass-600'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        <span>{benefit.trim()}</span>
                      </div>
                    ))}
                  </div>

                  <Button 
                    variant={isPlatinum ? "brass" : "outline"} 
                    className={`mt-10 w-full ${isPlatinum ? 'shadow-lg shadow-brass-500/20' : 'bg-white hover:bg-ink-50'}`}
                    as={Link}
                    to="/contact"
                  >
                    Enquire Now
                  </Button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
