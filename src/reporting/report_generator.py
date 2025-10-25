"""
Report Generator - Creates structured reports with JSON and human-readable formats
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from ..analytics.analytics_engine import AnalyticsEngine


class ReportGenerator:
    """
    Generates comprehensive reports from playtesting data
    """
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
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
        
        # Generate human-readable report
        human_readable_report = self.create_human_readable_report(json_report)
        text_path = os.path.join(report_dir, "human_readable_report.txt")
        with open(text_path, 'w') as f:
            f.write(human_readable_report)
        
        # Generate LLM-friendly summary for fun assessment
        llm_summary = self.create_llm_summary(json_report)
        llm_path = os.path.join(report_dir, "llm_summary.json")
        with open(llm_path, 'w') as f:
            json.dump(llm_summary, f, indent=2)
        
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
    
    def create_human_readable_report(self, json_report: Dict[str, Any]) -> str:
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
        
        return "\n".join(report_lines)
    
    def create_llm_summary(self, json_report: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary suitable for LLM processing"""
        # Extract key metrics for LLM assessment
        agg_metrics = json_report['aggregated_metrics']
        
        llm_summary = {
            'summary': {
                'total_agents': json_report['metadata']['total_agents'],
                'total_issues': agg_metrics['total_issues_detected'],
                'total_deaths': json_report['metadata']['total_deaths'],
                'total_retries': json_report['metadata']['total_retries'],
                'issues_by_type': agg_metrics['issues_by_type'],
                'anomalies_count': len(json_report['anomalies'])
            },
            'critical_issues': self._identify_critical_issues(json_report['anomalies']),
            'engagement_assessment': self._assess_engagement(
                agg_metrics['average_retries_per_agent'],
                json_report['metadata']['total_deaths']
            ),
            'fun_assessment_prompt': self._create_fun_assessment_prompt(json_report)
        }
        
        return llm_summary
    
    def _identify_critical_issues(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify critical issues from anomalies"""
        critical_types = {'softlock', 'infinite_loop', 'crash'}
        critical_issues = []
        
        for anomaly in anomalies:
            if anomaly.get('type') in critical_types:
                critical_issues.append(anomaly)
        
        return critical_issues
    
    def _assess_engagement(self, avg_retries: float, total_deaths: int) -> str:
        """Assess engagement level based on metrics"""
        engagement_level = "unknown"
        
        if avg_retries < 0.5 and total_deaths < 2:
            engagement_level = "potentially low - game might be too easy or unengaging"
        elif 0.5 <= avg_retries <= 2.0 and 2 <= total_deaths <= 10:
            engagement_level = "healthy - appropriate challenge level"
        elif 2.0 < avg_retries <= 5.0 or 10 < total_deaths <= 20:
            engagement_level = "high frustration risk - too challenging"
        else:
            engagement_level = "unbalanced - extreme challenge levels"
        
        return engagement_level
    
    def _create_fun_assessment_prompt(self, json_report: Dict[str, Any]) -> str:
        """Create a prompt for LLM-based fun assessment"""
        agg_metrics = json_report['aggregated_metrics']
        
        prompt = f"""
        Please assess the fun/engagement level of this game based on the following playtesting data:

        - Total agents: {json_report['metadata']['total_agents']}
        - Total issues detected: {agg_metrics['total_issues_detected']}
        - Issues by type: {agg_metrics['issues_by_type']}
        - Average retries per agent: {agg_metrics['average_retries_per_agent']:.2f}
        - Total deaths: {json_report['metadata']['total_deaths']}
        - Anomalies detected: {len(json_report['anomalies'])}

        Based on these metrics, assess:
        1. Is the game engaging?
        2. Is it appropriately challenging?
        3. Are there any major obstacles to fun?
        4. What improvements would you suggest?
        """
        
        return prompt