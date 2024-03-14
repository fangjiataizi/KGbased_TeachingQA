import React from "react";
import { createRoot } from "react-dom/client";

import "@neo4j-ndl/base/lib/neo4j-ds-styles.css";
import "./index.css";

const container = document.getElementById("root");
const root = createRoot(container!);

root.render(
  <React.StrictMode>
    <div className="flex flex-col min-h-screen gap-4 max-w-[1000px] w-[80%] mx-auto mt-4 ">
      <h1 className="text-4xl font-bold text-center">教学活动知识图谱</h1>
      <p>
        在这个项目中，我们基于知识图谱+大模型构建教学活动设计方面的问答系统。
      </p>
      <p>欢迎使用下述功能.</p>
      <div className="flex flex-col w-full gap-4 px-10">
        <a
          href="use-cases/chat-with-kg/index.html"
          className="ndl-btn ndl-large ndl-filled ndl-primary n-bg-palette-primary-bg-strong"
        >
          知识问答
        </a>
{/*         <a */}
{/*           href="use-cases/unstructured-import/index.html" */}
{/*           className="ndl-btn ndl-large ndl-filled ndl-primary n-bg-palette-primary-bg-strong" */}
{/*         > */}
{/*          非结构化数据导入 */}
{/*         </a> */}
{/*         <a */}
{/*           href="use-cases/report-generation/index.html" */}
{/*           className="ndl-btn ndl-large ndl-filled ndl-primary n-bg-palette-primary-bg-strong" */}
{/*         > */}
{/*           Report generator */}
{/*         </a> */}
      </div>
    </div>
  </React.StrictMode>
);
