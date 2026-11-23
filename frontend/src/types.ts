export type Dataset = {
  id: number;
  name: string;
  source_type: string;
  owner: string;
  description: string;
  status: string;
  created_at: string;
};

export type QualityCheck = {
  id: number;
  dataset_id: number;
  name: string;
  check_type: string;
  column_name: string;
  threshold: number;
  status: "passed" | "failed" | "running" | "pending";
};

export type QualityRun = {
  id: number;
  check_id: number;
  check_name: string;
  dataset_name: string;
  status: "passed" | "failed";
  score: number;
  message: string;
  executed_at: string;
};

export type Dashboard = {
  dataset_count: number;
  check_count: number;
  passed: number;
  failed: number;
  average_score: number;
};
