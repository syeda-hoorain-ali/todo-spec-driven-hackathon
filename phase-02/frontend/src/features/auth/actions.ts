"use server";

import { auth } from "@/lib/auth/server";
import {
  ChangePasswordFormData,
  ForgotPasswordFormData,
  ProfileFormData,
  ResetPasswordFormData,
  SignInFormData,
  SignUpFormData
} from "./schema";
import { headers } from "next/headers";
import { env } from "@/utils/env";


export async function signUpAction({ name, email, password }: SignUpFormData) {
  await auth.api.signUpEmail({
    body: {
      name,
      email,
      password,
      rememberMe: true
    }
  })
}


export async function signInAction({ email, password }: SignInFormData) {
  await auth.api.signInEmail({
    body: {
      email,
      password,
    },
  });
}

export async function signOutAction() {
  await auth.api.signOut({
    headers: await headers(),
  });
}

export async function forgotPasswordAction({ email }: ForgotPasswordFormData) {
  await auth.api.requestPasswordReset({
    body: {
      email,
      redirectTo: env.NEXT_PUBLIC_BASE_URL + "/reset-password",
    },
    headers: await headers(),
  })
}

export async function resetPasswordAction(
  { password, token }: ResetPasswordFormData & { token: string }
) {
  await auth.api.resetPassword({
    body: {
      newPassword: password,
      token
    },
    headers: await headers(),
  })
}

export async function updateUserAction({ name }: ProfileFormData) {
  await auth.api.updateUser({
    body: { name },
    headers: await headers(),
  })
}

export async function changePasswordAction({ currentPassword, newPassword }: ChangePasswordFormData) {
  await auth.api.changePassword({
    body: {
      currentPassword,
      newPassword,
      revokeOtherSessions: true
    },
    headers: await headers(),
  })
}
