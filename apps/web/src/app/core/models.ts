export interface ApiFailure {
  code: string;
  message: string;
  fields?: Record<string, string[]>;
}

export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Profile {
  id: string;
  email: string;
  phone: string | null;
  first_name: string;
  last_name: string;
  role: 'client' | 'professional';
  is_verified: boolean;
  client_profile_id?: string;
  company_name?: string;
  professional_profile_id?: string;
  business_name?: string;
  badge_verified?: boolean;
  verification_status?: string;
}

export interface Tokens {
  access: string;
  refresh: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
}

export interface Trade {
  id: string;
  category: string;
  name: string;
  slug: string;
  is_active: boolean;
}

export interface Specialty {
  id: string;
  trade: string;
  name: string;
  slug: string;
  is_active: boolean;
}

export interface Zone {
  id: string;
  region: string;
  city: string;
  district: string;
  is_active: boolean;
}

export interface ProfessionalCard {
  id: string;
  business_name: string;
  biography: string;
  years_of_experience: number | null;
  is_verified: boolean;
  average_rating: string | number;
  zones: Zone[];
}

export interface ProService {
  id: string;
  trade: string;
  specialty: string | null;
  title: string;
  description: string;
  starting_price: string;
  is_active: boolean;
}

export interface Availability {
  id: string;
  weekday: number;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export interface PortfolioItem {
  id: string;
  trade: string;
  specialty: string | null;
  zone: string | null;
  title: string;
  description: string;
  status: string;
  media: { id: string; media_type: string; file_key: string; display_order: number }[];
  created_at: string;
}

export interface PublicReview {
  id: string;
  rating: number;
  comment: string;
  professional_reply: string;
  created_at: string;
}

export interface ProfessionalDetail extends ProfessionalCard {
  services: ProService[];
  availabilities: Availability[];
  portfolio: PortfolioItem[];
  reviews: PublicReview[];
}

export interface ServiceRequest {
  id: string;
  zone: string;
  title: string;
  description: string;
  status: string;
  urgency: string;
  budget: string | null;
  desired_date: string | null;
  recipients: {
    id: string;
    professional: string;
    professional_name: string;
    status: string;
    decline_reason: string;
    created_at: string;
  }[];
  created_at: string;
}

export interface QuoteLine {
  id?: string;
  label: string;
  quantity: string;
  unit_price: string;
}

export interface Quote {
  id: string;
  recipient: string;
  service_request: string;
  total_amount: string;
  status: string;
  estimated_delay: string;
  conditions: string;
  expires_at: string | null;
  lines: QuoteLine[];
  created_at: string;
}

export interface Booking {
  id: string;
  quote: string;
  service_request: string;
  client: string;
  professional: string;
  status: string;
  scheduled_at: string | null;
  completed_at: string | null;
  created_at: string;
  conversation_id: string | null;
}

export interface ChatMessage {
  id: string;
  sender: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface Review {
  id: string;
  booking: string;
  rating: number;
  comment: string;
  professional_reply: string;
  status: string;
  editable_until: string | null;
  created_at: string;
}

export interface Address {
  id: string;
  label: string;
  city: string;
  district: string;
  latitude: string | null;
  longitude: string | null;
}

export interface Favorite {
  id: string;
  professional: string;
  name: string;
}

export interface Notice {
  id: string;
  kind: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

export interface DeviceSession {
  id: string;
  user_agent: string;
  ip_address: string | null;
  revoked_at: string | null;
  created_at: string;
}

export interface SupportTicket {
  id: string;
  subject: string;
  status: string;
  priority: string;
}

export interface VerificationCase {
  id?: string;
  status: string;
  admin_comment?: string;
  documents: { id: string; document_type: string; original_name: string }[];
}
