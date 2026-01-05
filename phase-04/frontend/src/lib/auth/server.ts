import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins"
import { nextCookies } from "better-auth/next-js";
import { sendPasswordResetEmail, sendVerificationEmail } from "@/lib/email/send";
import { env } from "@/utils/env";
import { BetterAuthOptions } from "@better-auth/core";
import { db } from "../database";

export const auth = betterAuth<BetterAuthOptions>({
  baseURL: env.NEXT_PUBLIC_BASE_URL,
  secret: env.BETTER_AUTH_SECRET,
  database: { db, casing: "snake" },
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

