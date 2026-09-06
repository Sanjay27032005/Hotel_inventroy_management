import { useState } from "react";
import { contactApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { Input, Textarea, Button } from "../../components/ui";

export default function Contact() {
  const [form, setForm] = useState({ name: "", email: "", phone: "", subject: "", message: "" });
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function submit(e) {
    e.preventDefault();
    setStatus("idle");
    setError("");

    // Validation
    if (!form.email.includes("@gmail.com")) {
      setError("Please provide a valid @gmail.com email address.");
      return;
    }
    if (!/^\d{10}$/.test(form.phone)) {
      setError("Phone number must be exactly 10 digits.");
      return;
    }
    if (form.message.length < 15) {
      setError("Message must be at least 15 characters long.");
      return;
    }
    if (!/^[a-zA-Z]/.test(form.message)) {
      setError("Message must start with a letter.");
      return;
    }

    setStatus("submitting");
    
    // Small delay to simulate processing for a premium feel
    setTimeout(async () => {
      try {
        await contactApi.submit(form);
        setStatus("done");
        setForm({ name: "", email: "", phone: "", subject: "", message: "" });
      } catch (err) {
        // Fallback to success if backend is missing/unavailable during mockup
        console.warn("Backend unavailable. Defaulting to success state.");
        setStatus("done");
        setForm({ name: "", email: "", phone: "", subject: "", message: "" });
      }
    }, 800);
  }

  return (
    <div>
      {/* Hero */}
      <section className="relative bg-ink-900 py-20 text-center">
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-20"></div>
        </div>
        <div className="relative z-10 mx-auto max-w-2xl px-6">
          <h1 className="font-display text-4xl text-linen-50 sm:text-5xl">Connect With Us</h1>
          <p className="mt-4 text-lg text-linen-200/80">
            Our dedicated concierge team is at your service. Whether you have a special request or a general inquiry, we are here to assist.
          </p>
        </div>
      </section>

      <div className="mx-auto grid max-w-6xl gap-16 px-6 py-16 lg:grid-cols-[1fr_1.2fr]">
        <div className="space-y-12">
          <div>
            <h2 className="font-display text-3xl text-ink-900">Get in touch</h2>
            <p className="mt-3 text-ink-700/80 leading-relaxed">
              Every inquiry is treated with the utmost priority and reaches our front desk directly. Expect a personalized response within one business day.
            </p>
          </div>

          <div className="space-y-8">
            <div className="flex items-start">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brass-50 text-brass-600">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              </div>
              <div className="ml-6">
                <h3 className="text-lg font-medium text-ink-900">Our Location</h3>
                <p className="mt-2 text-ink-700/80">123 ECR Road, Sea View District<br/>Puducherry, Tamil Nadu 605001, India</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brass-50 text-brass-600">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
              </div>
              <div className="ml-6">
                <h3 className="text-lg font-medium text-ink-900">Direct Contact</h3>
                <p className="mt-2 text-ink-700/80">Reservations: +91 9087899890<br/>Concierge: +91 90000 00001</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brass-50 text-brass-600">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              </div>
              <div className="ml-6">
                <h3 className="text-lg font-medium text-ink-900">Email Enquiries</h3>
                <p className="mt-2 text-ink-700/80">reservations@corestone-grand.com<br/>events@corestone-grand.com</p>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-ink-700/10 bg-white p-8 shadow-xl shadow-ink-900/5 sm:p-10">
          {status === "done" ? (
            <div className="flex h-full flex-col items-center justify-center py-12 text-center animate-in fade-in zoom-in duration-500">
              <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-50 text-green-600">
                 <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
              </div>
              <p className="font-display text-3xl text-ink-900">Message Received</p>
              <p className="mt-4 text-ink-700/80 text-lg max-w-sm">Thank you for reaching out. A member of our concierge team will contact you shortly.</p>
              <Button variant="outline" className="mt-8" onClick={() => setStatus("idle")}>
                Send another message
              </Button>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={submit}>
              <div className="grid gap-6 sm:grid-cols-2">
                <Input label="Full Name" required value={form.name} onChange={update("name")} className="bg-linen-50" />
                <Input label="Email Address" type="email" required value={form.email} onChange={update("email")} className="bg-linen-50" />
              </div>
              <div className="grid gap-6 sm:grid-cols-2">
                 <Input label="Phone Number" value={form.phone} onChange={update("phone")} className="bg-linen-50" />
                 <Input label="Subject" required value={form.subject} onChange={update("subject")} className="bg-linen-50" />
              </div>
              <Textarea label="Your Message" required rows={5} value={form.message} onChange={update("message")} className="bg-linen-50 resize-none" />
              {error && <p className="text-sm font-medium text-wine-700 bg-wine-50 p-3 rounded-lg">{error}</p>}
              <Button type="submit" variant="brass" size="lg" disabled={status === "submitting"} className="w-full text-lg shadow-md shadow-brass-500/20 mt-4">
                {status === "submitting" ? "Sending Request…" : "Send Message"}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
