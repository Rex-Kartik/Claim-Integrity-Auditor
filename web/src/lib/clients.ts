import type { RunClient } from "./runClient";
import { HttpRunClient } from "./httpRunClient";

export const runClient: RunClient = new HttpRunClient();
