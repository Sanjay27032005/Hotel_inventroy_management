import client, { API_BASE_URL } from "./client";

// ---------- Auth ----------
export const authApi = {
  login: (username, password) => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return client.post("/api/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => client.get("/api/auth/me"),
};

// ---------- Customers ----------
export const customerApi = {
  register: (payload) => client.post("/api/customers/register", payload),
  me: () => client.get("/api/customers/me"),
  list: (search) => client.get("/api/customers", { params: { search } }),
  get: (id) => client.get(`/api/customers/${id}`),
  update: (id, payload) => client.put(`/api/customers/${id}`, payload),
};

// ---------- Employees ----------
export const employeeApi = {
  listDepartments: () => client.get("/api/employees/departments"),
  createDepartment: (payload) => client.post("/api/employees/departments", payload),
  list: (params) => client.get("/api/employees", { params }),
  get: (id) => client.get(`/api/employees/${id}`),
  create: (payload) => client.post("/api/employees", payload),
  createAccount: (id, username, password) =>
    client.post(`/api/employees/${id}/create-account`, null, { params: { username, password } }),
  update: (id, payload) => client.put(`/api/employees/${id}`, payload),
  deactivate: (id) => client.delete(`/api/employees/${id}`),
};

// ---------- Destinations ----------
export const destinationApi = {
  countries: () => client.get("/api/destinations/countries"),
  states: (countryId) => client.get(`/api/destinations/countries/${countryId}/states`),
  cities: (stateId) => client.get(`/api/destinations/states/${stateId}/cities`),
  hotels: (cityId) => client.get("/api/destinations/hotels", { params: { city_id: cityId } }),
  hotel: (id) => client.get(`/api/destinations/hotels/${id}`),
};

// ---------- Membership ----------
export const membershipApi = {
  plans: () => client.get("/api/membership/plans"),
  createPlan: (payload) => client.post("/api/membership/plans", payload),
  enroll: (payload) => client.post("/api/membership/enroll", payload),
  forCustomer: (customerId) => client.get(`/api/membership/customer/${customerId}`),
};

// ---------- Rooms / Accommodation ----------
export const roomApi = {
  types: () => client.get("/api/rooms/types"),
  createType: (payload) => client.post("/api/rooms/types", payload),
  list: (params) => client.get("/api/rooms", { params }),
  create: (payload) => client.post("/api/rooms", payload),
  updateStatus: (id, newStatus) =>
    client.put(`/api/rooms/${id}/status`, null, { params: { new_status: newStatus } }),
  checkAvailability: (roomId, checkIn, checkOut) =>
    client.get("/api/rooms/availability", {
      params: { room_id: roomId, check_in_date: checkIn, check_out_date: checkOut },
    }),
  bookings: (params) => client.get("/api/rooms/bookings", { params }),
  bookingDetail: (id) => client.get(`/api/rooms/bookings/${id}`),
  book: (payload) => client.post("/api/rooms/bookings", payload),
  checkIn: (id) => client.post(`/api/rooms/bookings/${id}/check-in`),
  checkOut: (id) => client.post(`/api/rooms/bookings/${id}/check-out`),
  cancel: (id) => client.post(`/api/rooms/bookings/${id}/cancel`),
};

// ---------- Restaurant ----------
export const restaurantApi = {
  tables: (params) => client.get("/api/restaurant/tables", { params }),
  createTable: (payload) => client.post("/api/restaurant/tables", payload),
  updateTableStatus: (id, newStatus) =>
    client.put(`/api/restaurant/tables/${id}/status`, null, { params: { new_status: newStatus } }),
  bookTable: (payload) => client.post("/api/restaurant/bookings", payload),
  tableBookings: (params) => client.get("/api/restaurant/bookings", { params }),
  categories: () => client.get("/api/restaurant/categories"),
  createCategory: (payload) => client.post("/api/restaurant/categories", payload),
  menu: (params) => client.get("/api/restaurant/menu", { params }),
  createFoodItem: (payload) => client.post("/api/restaurant/menu", payload),
  orders: (params) => client.get("/api/restaurant/orders", { params }),
  orderDetail: (id) => client.get(`/api/restaurant/orders/${id}`),
  createOrder: (payload) => client.post("/api/restaurant/orders", payload),
  updateOrderStatus: (id, newStatus) =>
    client.put(`/api/restaurant/orders/${id}/status`, null, { params: { new_status: newStatus } }),
};

// ---------- Party Hall ----------
export const partyHallApi = {
  eventTypes: () => client.get("/api/party-hall/event-types"),
  createEventType: (name) => client.post("/api/party-hall/event-types", null, { params: { name } }),
  halls: () => client.get("/api/party-hall/halls"),
  createHall: (payload) => client.post("/api/party-hall/halls", payload),
  bookings: (params) => client.get("/api/party-hall/bookings", { params }),
  book: (payload) => client.post("/api/party-hall/bookings", payload),
  cancel: (id) => client.post(`/api/party-hall/bookings/${id}/cancel`),
};

// ---------- Swimming Pool ----------
export const poolApi = {
  prices: () => client.get("/api/pool/prices"),
  setPrice: (payload) => client.put("/api/pool/prices", payload),
  trainers: () => client.get("/api/pool/trainers"),
  createTrainer: (name, specialization) =>
    client.post("/api/pool/trainers", null, { params: { name, specialization } }),
  bookings: (params) => client.get("/api/pool/bookings", { params }),
  book: (payload) => client.post("/api/pool/bookings", payload),
};

// ---------- Spa ----------
export const spaApi = {
  services: () => client.get("/api/spa/services"),
  createService: (payload) => client.post("/api/spa/services", payload),
  therapists: () => client.get("/api/spa/therapists"),
  createTherapist: (name, specialization) =>
    client.post("/api/spa/therapists", null, { params: { name, specialization } }),
  bookings: (params) => client.get("/api/spa/bookings", { params }),
  book: (payload) => client.post("/api/spa/bookings", payload),
};

// ---------- Club & Bar ----------
export const clubApi = {
  createMembership: (payload) => client.post("/api/club/memberships", payload),
  foodItems: () => client.get("/api/club/food-items"),
  createFoodItem: (payload) => client.post("/api/club/food-items", payload),
  drinkItems: () => client.get("/api/club/drink-items"),
  createDrinkItem: (payload) => client.post("/api/club/drink-items", payload),
  orders: (params) => client.get("/api/club/orders", { params }),
  createOrder: (payload) => client.post("/api/club/orders", payload),
};

// ---------- Laundry ----------
export const laundryApi = {
  prices: () => client.get("/api/laundry/prices"),
  setPrice: (payload) => client.put("/api/laundry/prices", payload),
  orders: (params) => client.get("/api/laundry/orders", { params }),
  createOrder: (payload) => client.post("/api/laundry/orders", payload),
  updateStatus: (id, newStatus) =>
    client.put(`/api/laundry/orders/${id}/status`, null, { params: { new_status: newStatus } }),
};

// ---------- Bookings (central) ----------
export const bookingApi = {
  lookup: (params) => client.get("/api/bookings/lookup", { params }),
  detail: (id) => client.get(`/api/bookings/${id}/detail`),
  cancel: (id) => client.post(`/api/bookings/${id}/cancel`),
  submitStayRequest: (payload) => client.post("/api/bookings/stay-requests", payload),
  stayRequests: (params) => client.get("/api/bookings/stay-requests", { params }),
  updateStayRequestStatus: (id, newStatus) =>
    client.put(`/api/bookings/stay-requests/${id}/status`, null, { params: { new_status: newStatus } }),
};

// ---------- Billing ----------
export const billingApi = {
  generateInvoice: (serviceType, referenceId) =>
    client.post("/api/billing/invoices/generate", { service_type: serviceType, reference_id: referenceId }),
  invoices: (params) => client.get("/api/billing/invoices", { params }),
  invoice: (id) => client.get(`/api/billing/invoices/${id}`),
  invoicePdfUrl: (id) => `${API_BASE_URL}/api/billing/invoices/${id}/pdf`,
  pay: (payload) => client.post("/api/billing/payments", payload),
  refund: (id) => client.post(`/api/billing/invoices/${id}/refund`),
};

// ---------- Dashboard & Reports ----------
export const dashboardApi = {
  kpis: () => client.get("/api/dashboard/kpis"),
  revenueTrend: (days) => client.get("/api/dashboard/revenue-trend", { params: { days } }),
};

export const reportsApi = {
  get: (path, params) => client.get(`/api/reports/${path}`, { params }),
};

// ---------- Gallery / Contact / Content / Notifications ----------
export const galleryApi = {
  list: (category) => client.get("/api/gallery", { params: { category } }),
  add: (payload) => client.post("/api/gallery", payload),
};

export const contactApi = {
  submit: (payload) => client.post("/api/contact", payload),
  list: (params) => client.get("/api/contact", { params }),
  updateStatus: (id, newStatus) =>
    client.put(`/api/contact/${id}/status`, null, { params: { new_status: newStatus } }),
};

export const contentApi = {
  offers: () => client.get("/api/content/offers"),
  createOffer: (payload) => client.post("/api/content/offers", payload),
  travelStories: () => client.get("/api/content/travel-stories"),
  createTravelStory: (payload) => client.post("/api/content/travel-stories", payload),
  infoPages: () => client.get("/api/content/info-pages"),
  infoPage: (slug) => client.get(`/api/content/info-pages/${slug}`),
};

export const notificationApi = {
  mine: () => client.get("/api/notifications/me"),
  markRead: (id) => client.put(`/api/notifications/${id}/read`),
};
