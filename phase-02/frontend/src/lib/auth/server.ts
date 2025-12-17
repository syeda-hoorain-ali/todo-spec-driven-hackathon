import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins"
import { nextCookies } from "better-auth/next-js";
import { Pool } from "pg";
import { sendPasswordResetEmail, sendVerificationEmail } from "@/lib/email/send";
import { env } from "@/utils/env";

// Create a singleton pool to avoid multiple connections
let pool: Pool | null = null;

function getPool() {
  if (!pool) {
    pool = new Pool({
      connectionString: env.DATABASE_URL,
      max: 10, // Maximum number of clients in the pool
      idleTimeoutMillis: env.DB_IDLE_TIMEOUT || 30000,
      connectionTimeoutMillis: env.DB_CONNECT_TIMEOUT || 10000,
      keepAlive: true,
      ssl: {
        rejectUnauthorized: false // Neon requires SSL
      }
    });

    // Handle pool errors
    pool.on('error', (err) => {
      console.error('Unexpected database pool error:', err);
    });
  }
  return pool;
}

export const auth = betterAuth({
  baseURL: env.NEXT_PUBLIC_BASE_URL,
  secret: env.BETTER_AUTH_SECRET,
  database: getPool(),
  emailVerification: {
    async sendVerificationEmail({ user, url }) {
      const emailSent = await sendVerificationEmail(user.email, url, user.name);
      if (!emailSent) {
        throw new Error("Failed to send email verification email");
      }
    },
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
    async sendResetPassword({ user, url }) {
      const emailSent = await sendPasswordResetEmail(user.email, url, user.name);
      if (!emailSent) {
        throw new Error("Failed to send password reset email");
      }
    },
    resetPasswordTokenExpiresIn: 3600
  },
  socialProviders: {},
  plugins: [
    nextCookies(),
    jwt(),
  ],
  advanced: {
    defaultCookieAttributes: {
      httpOnly: true,
      secure: env.NODE_ENV === "production"
    },
  }
});

