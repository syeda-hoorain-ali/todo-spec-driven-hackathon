import { env } from "@/utils/env";
import { neon } from "@neondatabase/serverless";
import { Kysely } from "kysely";
import { NeonDialect } from "kysely-neon";

export interface Database { }

export const db = new Kysely<Database>({
    dialect: new NeonDialect({
        neon: neon(env.DATABASE_URL),
    }),
});
