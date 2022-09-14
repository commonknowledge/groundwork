import { startApp } from "../../frontend/index.lib";
const controllers = import.meta.glob("./controllers/*-controller.ts");

startApp(controllers);
