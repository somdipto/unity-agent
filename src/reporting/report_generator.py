"""
Report Generator - Creates structured reports with JSON and human-readable formats
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..analytics.analytics_engine import AnalyticsEngine
from .llm_analyzer import LLMAnalyzer


class ReportGenerator:
    """
    Generates comprehensive reports from playtesting data
    """
    
    def __init__(self, output_dir: str = "./reports", llm_analyzer: Optional[LLMAnalyzer] = None):
        self.output_dir = output_dir
        self.llm_analyzer = llm_analyzer
        self.ensure_output_directory()
        
    def ensure_output_directory(self):
        """Ensure the output directory exists"""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_comprehensive_report(self, test_results: List[Dict[str, Any]]):
        """Generate a comprehensive report from test results"""
        # Create timestamped report directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(self.output_dir, f"report_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate structured JSON report
        json_report = self.create_json_report(test_results)
        json_path = os.path.join(report_dir, "structured_report.json")
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)
        
        # Generate LLM insights if analyzer is available
        llm_insights = {}
        narrative_report = ""
        
        if self.llm_analyzer:
            print("Generating LLM insights...")
            try:
                # Generate structured assessments
                fun_assessment = self.llm_analyzer.assess_fun_factor(json_report)
                improvements = self.llm_analyzer.suggest_improvements(json_report)
                narrative_report = self.llm_analyzer.generate_narrative_report(json_report)
                
                llm_insights = {
                    "fun_assessment": fun_assessment,
                    "improvements": improvements,
                    "narrative_report": narrative_report
                }
                
                # Save structured LLM insights
                insights_path = os.path.join(report_dir, "llm_insights.json")
                with open(insights_path, 'w') as f:
                    json.dump(llm_insights, f, indent=2)
                    
            except Exception as e:
                print(f"Error generating LLM insights: {e}")
        
        # Generate human-readable report (including LLM narrative if available)
        human_readable_report = self.create_human_readable_report(json_report, narrative_report)
        text_path = os.path.join(report_dir, "human_readable_report.txt")
        with open(text_path, 'w') as f:
            f.write(human_readable_report)
        
        print(f"Reports generated in: {report_dir}")
        
    def create_json_report(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a structured JSON report"""
        # Aggregate results from all agents
        all_issues = []
        total_deaths = 0
        total_retries = 0
        total_time = 0
        
        for agent_result in test_results:
            all_issues.extend(agent_result.get('issues_detected', []))
            total_deaths += agent_result.get('deaths', 0)
            total_retries += agent_result.get('retries', 0)
            total_time += agent_result.get('time_spent', 0)
        
        # Create the report structure
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_agents': len(test_results),
                'total_test_time': total_time,
                'total_deaths': total_deaths,
                'total_retries': total_retries
            },
            'individual_agent_reports': test_results,
            'aggregated_metrics': {
                'total_issues_detected': len(all_issues),
                'issues_by_type': self._categorize_issues(all_issues),
                'average_retries_per_agent': total_retries / max(1, len(test_results)),
                'average_deaths_per_agent': total_deaths / max(1, len(test_results))
            },
            'detected_issues': all_issues,
            'anomalies': self._extract_anomalies(all_issues)
        }
        
        return report
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count issues by type"""
        categories = {}
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            categories[issue_type] = categories.get(issue_type, 0) + 1
        return categories
    
    def _extract_anomalies(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract anomalies from issues"""
        anomalies = []
        anomaly_types = {'softlock', 'infinite_loop', 'crash', 'performance_issue'}
        
        for issue in issues:
            if issue.get('type') in anomaly_types:
                anomalies.append(issue)
        
        return anomalies
    
    def create_human_readable_report(self, json_report: Dict[str, Any], narrative_report: str = "") -> str:
        """Create a human-readable report from JSON data"""
        report_lines = []
        report_lines.append("AI Playtesting System - Human-Readable Report")
        report_lines.append("=" * 50)
        report_lines.append("")
        
        # Add metadata
        metadata = json_report['metadata']
        report_lines.append("Test Session Summary")
        report_lines.append("-" * 20)
        report_lines.append(f"Generated At: {metadata['generated_at']}")
        report_lines.append(f"Total Agents: {metadata['total_agents']}")
        report_lines.append(f"Total Test Time: {metadata['total_test_time']:.2f} seconds")
        report_lines.append(f"Total Deaths: {metadata['total_deaths']}")
        report_lines.append(f"Total Retries: {metadata['total_retries']}")
        report_lines.append("")
        
        # Add aggregated metrics
        agg_metrics = json_report['aggregated_metrics']
        report_lines.append("Aggregated Metrics")
        report_lines.append("-" * 18)
        report_lines.append(f"Total Issues Detected: {agg_metrics['total_issues_detected']}")
        report_lines.append(f"Average Retries per Agent: {agg_metrics['average_retries_per_agent']:.2f}")
        report_lines.append(f"Average Deaths per Agent: {agg_metrics['average_deaths_per_agent']:.2f}")
        report_lines.append("")
        
        # Add issue breakdown
        if agg_metrics['issues_by_type']:
            report_lines.append("Issues by Type")
            report_lines.append("-" * 15)
            for issue_type, count in agg_metrics['issues_by_type'].items():
                report_lines.append(f"  {issue_type}: {count}")
            report_lines.append("")
        
        # Add anomalies
        anomalies = json_report['anomalies']
        if anomalies:
            report_lines.append("Anomalies Detected")
            report_lines.append("-" * 18)
            for i, anomaly in enumerate(anomalies, 1):
                report_lines.append(f"{i}. Type: {anomaly.get('type', 'unknown')}")
                report_lines.append(f"   Timestamp: {anomaly.get('timestamp', 'unknown')}")
                report_lines.append(f"   Details: {anomaly.get('details', 'N/A')}")
                report_lines.append("")
        
        # Add high-level assessment
        report_lines.append("High-Level Assessment")
        report_lines.append("-" * 21)
        total_issues = agg_metrics['total_issues_detected']
        if total_issues == 0:
            report_lines.append("No issues were detected during testing.")
        elif total_issues < 5:
            report_lines.append("Few issues detected, game appears stable.")
        elif total_issues < 15:
            report_lines.append("Moderate number of issues detected, review recommended.")
        else:
            report_lines.append("High number of issues detected, significant review needed.")
        
        # Add engagement assessment
        avg_retries = agg_metrics['average_retries_per_agent']
        if avg_retries > 3:
            report_lines.append("High retry rate suggests potential frustration points in the game.")
        elif avg_retries > 1:
            report_lines.append("Moderate retry rate, some challenges may be appropriately difficult.")
        else:
            report_lines.append("Low retry rate, game may be too easy or lacking challenge.")
        
        # Append LLM Narrative if available
        if narrative_report:
            report_lines.append("")
            report_lines.append("AI Experience Narrative")
            report_lines.append("-" * 23)
            report_lines.append(narrative_report)
            report_lines.append("")

        return "\n".join(report_lines)