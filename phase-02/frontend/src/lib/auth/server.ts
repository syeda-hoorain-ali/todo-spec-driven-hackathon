import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "pg";
import { sendPasswordResetEmail, sendVerificationEmail } from "@/lib/email/send";
import { env } from "@/utils/env";

export const auth = betterAuth({
  baseURL: env.NEXT_PUBLIC_BASE_URL,
  secret: env.BETTER_AUTH_SECRET,
  database: new Pool({
    connectionString: env.DATABASE_URL,
    idleTimeoutMillis: env.DB_IDLE_TIMEOUT,  // Maximum time (ms) a connection can sit idle in the pool
    connectionTimeoutMillis: env.DB_CONNECT_TIMEOUT,  // Maximum time (ms) to try to establish a connection
    query_timeout: env.DB_QUERY_TIMEOUT,  // Query timeout settings
    keepAlive: true,  // Enable keep alive for long-running connections
  }),
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
      if (emailSent) {
        throw new Error("Failed to send password reset email");
      }
    },
    resetPasswordTokenExpiresIn: 3600
  },
  socialProviders: {},
  plugins: [nextCookies()],
  advanced: {
    defaultCookieAttributes: {
      httpOnly: true,
      secure: true
    },
  }
});

