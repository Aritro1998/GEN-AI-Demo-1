# repository/analytics_service.py
"""
Analytics service for admin dashboard and reporting.
Handles KPIs, outbreak mapping, and trend analysis.
"""

from sqlalchemy.orm import Session
from sqlalchemy import Integer, func, and_, or_
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Dict, List
from models import DiagnosisRecord, AdminFeedback, User
from repository.ai_utils.logger import AILogger


class AnalyticsService:
    """Service for generating analytics and reports for admin dashboard"""
    
    def __init__(self):
        self.logger = AILogger()
    
    async def get_kpi_dashboard(self, db: Session) -> Dict:
        """
        Generate KPI dashboard data with key metrics.
        
        Returns:
            Dict with total diagnoses, top diseases, accuracy, hotspots
        """
        try:
            today = datetime.utcnow().date()
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            # Total diagnoses today and this week
            total_today = db.query(DiagnosisRecord).filter(
                func.date(DiagnosisRecord.timestamp) == today
            ).count()
            
            total_week = db.query(DiagnosisRecord).filter(
                DiagnosisRecord.timestamp >= week_ago
            ).count()
            
            # Total all time
            total_all_time = db.query(DiagnosisRecord).count()
            
            # Top 5 diseases
            top_diseases = db.query(
                DiagnosisRecord.diagnosis,
                func.count(DiagnosisRecord.id).label('count')
            ).filter(
                DiagnosisRecord.diagnosis != 'Healthy'
            ).group_by(
                DiagnosisRecord.diagnosis
            ).order_by(
                func.count(DiagnosisRecord.id).desc()
            ).limit(5).all()
            
            # Top 5 crops
            top_crops = db.query(
                DiagnosisRecord.crop,
                func.count(DiagnosisRecord.id).label('count')
            ).group_by(
                DiagnosisRecord.crop
            ).order_by(
                func.count(DiagnosisRecord.id).desc()
            ).limit(5).all()
            
            # System accuracy from admin feedback
            total_validated = db.query(AdminFeedback).count()
            correct_diagnoses = db.query(AdminFeedback).filter(
                AdminFeedback.is_correct == True
            ).count()
            accuracy = round((correct_diagnoses / total_validated * 100), 2) if total_validated > 0 else None
            
            # Average confidence score
            avg_confidence = db.query(
                func.avg(DiagnosisRecord.confidence_score)
            ).scalar()
            
            # Disease hotspots (locations with multiple cases)
            hotspots = db.query(
                DiagnosisRecord.latitude,
                DiagnosisRecord.longitude,
                DiagnosisRecord.diagnosis,
                func.count(DiagnosisRecord.id).label('count')
            ).filter(
                and_(
                    DiagnosisRecord.latitude.isnot(None),
                    DiagnosisRecord.longitude.isnot(None),
                    DiagnosisRecord.diagnosis != 'Healthy'
                )
            ).group_by(
                DiagnosisRecord.latitude,
                DiagnosisRecord.longitude,
                DiagnosisRecord.diagnosis
            ).having(
                func.count(DiagnosisRecord.id) >= 2  # At least 2 cases
            ).all()
            
            # Risk distribution
            risk_distribution = db.query(
                DiagnosisRecord.risk_level,
                func.count(DiagnosisRecord.id).label('count')
            ).filter(
                DiagnosisRecord.timestamp >= week_ago
            ).group_by(
                DiagnosisRecord.risk_level
            ).all()
            
            return {
                "total_diagnoses_today": total_today,
                "total_diagnoses_week": total_week,
                "total_diagnoses_all_time": total_all_time,
                "top_diseases": [
                    {"disease": d[0], "count": d[1]} for d in top_diseases
                ],
                "top_crops": [
                    {"crop": c[0], "count": c[1]} for c in top_crops
                ],
                "system_accuracy": accuracy,
                "average_confidence": round(avg_confidence, 2) if avg_confidence else None,
                "disease_hotspots": [
                    {
                        "lat": h[0],
                        "lng": h[1],
                        "disease": h[2],
                        "count": h[3]
                    } for h in hotspots
                ],
                "risk_distribution": {
                    r[0]: r[1] for r in risk_distribution
                },
                "total_active_users": db.query(User).filter(User.is_active == True).count(),
                "pending_validations": db.query(DiagnosisRecord).filter(
                    DiagnosisRecord.admin_validated == False
                ).count()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating KPI dashboard: {str(e)}")
            raise
    
    async def get_outbreak_map(
        self, 
        db: Session, 
        risk_level: Optional[str] = None,
        crop_filter: Optional[str] = None,
        days_back: int = 30
    ) -> Dict:
        """
        Generate outbreak prediction map data with clustering.
        
        Args:
            db: Database session
            risk_level: Filter by risk level
            crop_filter: Filter by crop type
            days_back: Number of days to look back
        
        Returns:
            Dict with map_points, clusters, and statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Build query
            query = db.query(DiagnosisRecord).filter(
                and_(
                    DiagnosisRecord.timestamp >= cutoff_date,
                    DiagnosisRecord.latitude.isnot(None),
                    DiagnosisRecord.longitude.isnot(None),
                    DiagnosisRecord.diagnosis != 'Healthy'
                )
            )
            
            if risk_level:
                query = query.filter(DiagnosisRecord.risk_level == risk_level)
            
            if crop_filter:
                query = query.filter(DiagnosisRecord.crop == crop_filter)
            
            records = query.all()
            
            # Group by approximate location (cluster nearby points)
            location_clusters = defaultdict(lambda: {
                "high": 0, "medium": 0, "low": 0, "critical": 0,
                "diseases": defaultdict(int),
                "crops": defaultdict(int),
                "latest_date": None
            })
            
            for record in records:
                # Round to 2 decimal places for clustering (~1km accuracy)
                loc_key = f"{record.latitude:.2f},{record.longitude:.2f}"
                cluster = location_clusters[loc_key]
                
                cluster[record.risk_level] += 1
                cluster["diseases"][record.diagnosis] += 1
                cluster["crops"][record.crop] += 1
                
                if cluster["latest_date"] is None or record.timestamp > cluster["latest_date"]:
                    cluster["latest_date"] = record.timestamp
            
            # Format for map visualization
            map_data = []
            for loc, cluster_info in location_clusters.items():
                lat, lng = loc.split(',')
                total = sum([cluster_info["high"], cluster_info["medium"], 
                            cluster_info["low"], cluster_info["critical"]])
                
                # Determine dominant risk
                risk_counts = {
                    "critical": cluster_info["critical"],
                    "high": cluster_info["high"],
                    "medium": cluster_info["medium"],
                    "low": cluster_info["low"]
                }
                dominant_risk = max(risk_counts, key=risk_counts.get)
                
                # Get most common disease and crop
                dominant_disease = max(cluster_info["diseases"], 
                                     key=cluster_info["diseases"].get)
                dominant_crop = max(cluster_info["crops"], 
                                   key=cluster_info["crops"].get)
                
                map_data.append({
                    "lat": float(lat),
                    "lng": float(lng),
                    "risk_level": dominant_risk,
                    "risk_counts": risk_counts,
                    "total_cases": total,
                    "dominant_disease": dominant_disease,
                    "dominant_crop": dominant_crop,
                    "all_diseases": dict(cluster_info["diseases"]),
                    "latest_date": cluster_info["latest_date"].isoformat()
                })
            
            # Sort by total cases (most affected areas first)
            map_data.sort(key=lambda x: x["total_cases"], reverse=True)
            
            # Calculate statistics
            high_risk_regions = sum(1 for m in map_data if m['risk_level'] in ['high', 'critical'])
            total_cases = sum(m['total_cases'] for m in map_data)
            
            return {
                "map_points": map_data,
                "total_regions": len(map_data),
                "high_risk_regions": high_risk_regions,
                "total_cases": total_cases,
                "filters_applied": {
                    "risk_level": risk_level or "all",
                    "crop": crop_filter or "all",
                    "days_back": days_back,
                    "date_range": {
                        "start": cutoff_date.isoformat(),
                        "end": datetime.utcnow().isoformat()
                    }
                },
                "summary": {
                    "most_affected_disease": max(
                        (m["dominant_disease"] for m in map_data),
                        key=lambda d: sum(m["total_cases"] for m in map_data if m["dominant_disease"] == d),
                        default="None"
                    ) if map_data else "None"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating outbreak map: {str(e)}")
            raise
    
    async def get_analytics_report(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Generate comprehensive analytics report with trends.
        
        Returns:
            Dict with disease trends, severity distribution, time series data
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=90)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Disease trends over time
            daily_trends = db.query(
                func.date(DiagnosisRecord.timestamp).label('date'),
                DiagnosisRecord.diagnosis,
                func.count(DiagnosisRecord.id).label('count')
            ).filter(
                and_(
                    DiagnosisRecord.timestamp >= start_date,
                    DiagnosisRecord.timestamp <= end_date
                )
            ).group_by(
                func.date(DiagnosisRecord.timestamp),
                DiagnosisRecord.diagnosis
            ).order_by(
                func.date(DiagnosisRecord.timestamp)
            ).all()
            
            # Severity distribution by disease
            severity_dist = db.query(
                DiagnosisRecord.diagnosis,
                func.avg(DiagnosisRecord.severity_percent).label('avg_severity'),
                func.max(DiagnosisRecord.severity_percent).label('max_severity'),
                func.count(DiagnosisRecord.id).label('count')
            ).filter(
                and_(
                    DiagnosisRecord.timestamp >= start_date,
                    DiagnosisRecord.timestamp <= end_date,
                    DiagnosisRecord.diagnosis != 'Healthy'
                )
            ).group_by(
                DiagnosisRecord.diagnosis
            ).all()
            
            # Crop-wise analysis
            crop_analysis = db.query(
                DiagnosisRecord.crop,
                func.count(DiagnosisRecord.id).label('total_cases'),
                func.avg(DiagnosisRecord.severity_percent).label('avg_severity'),
                func.sum(
                    func.cast(DiagnosisRecord.diagnosis != 'Healthy', Integer)
                ).label('diseased_count')
            ).filter(
                and_(
                    DiagnosisRecord.timestamp >= start_date,
                    DiagnosisRecord.timestamp <= end_date
                )
            ).group_by(
                DiagnosisRecord.crop
            ).all()
            
            # Weekly aggregation for trend visualization
            weekly_aggregation = db.query(
                func.date_trunc('week', DiagnosisRecord.timestamp).label('week'),
                func.count(DiagnosisRecord.id).label('total_cases'),
                func.sum(
                    func.cast(DiagnosisRecord.risk_level == 'high', Integer)
                ).label('high_risk_cases'),
                func.avg(DiagnosisRecord.severity_percent).label('avg_severity')
            ).filter(
                and_(
                    DiagnosisRecord.timestamp >= start_date,
                    DiagnosisRecord.timestamp <= end_date
                )
            ).group_by(
                func.date_trunc('week', DiagnosisRecord.timestamp)
            ).order_by(
                func.date_trunc('week', DiagnosisRecord.timestamp)
            ).all()
            
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": (end_date - start_date).days
                },
                "disease_trends": [
                    {
                        "date": str(t[0]),
                        "disease": t[1],
                        "count": t[2]
                    } for t in daily_trends
                ],
                "severity_distribution": [
                    {
                        "disease": s[0],
                        "average_severity": round(s[1], 2),
                        "max_severity": round(s[2], 2),
                        "case_count": s[3]
                    } for s in severity_dist
                ],
                "crop_analysis": [
                    {
                        "crop": c[0],
                        "total_cases": c[1],
                        "average_severity": round(c[2], 2) if c[2] else 0,
                        "diseased_count": c[3],
                        "health_rate": round((1 - c[3]/c[1]) * 100, 2) if c[1] > 0 else 100
                    } for c in crop_analysis
                ],
                "weekly_trends": [
                    {
                        "week": w[0].isoformat() if w[0] else None,
                        "total_cases": w[1],
                        "high_risk_cases": w[2] or 0,
                        "average_severity": round(w[3], 2) if w[3] else 0
                    } for w in weekly_aggregation
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating analytics report: {str(e)}")
            raise


# Singleton instance
_analytics_instance = None

def get_analytics_service() -> AnalyticsService:
    """Get or create singleton analytics service instance"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AnalyticsService()
    return _analytics_instance
