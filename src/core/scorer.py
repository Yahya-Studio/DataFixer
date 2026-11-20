"""Interpretable Data Quality Scorer."""

from config.settings import config
from src.core.schemas import QualityIssue, QualityScoreBreakdown


class QualityScorer:
    """Calculates an explainable Data Quality Score between 0.0 and 100.0.

    The score is decomposed into 4 pillars:
    - Completeness (30% default)
    - Uniqueness (20% default)
    - Validity (30% default)
    - Consistency (20% default)
    """

    @classmethod
    def calculate_score(
        cls,
        total_rows: int,
        total_cols: int,
        issues: list[QualityIssue],
    ) -> QualityScoreBreakdown:
        if total_rows == 0 or total_cols == 0:
            return QualityScoreBreakdown(
                overall_score=0.0,
                completeness=0.0,
                uniqueness=0.0,
                validity=0.0,
                consistency=0.0,
            )

        total_cells = total_rows * total_cols

        # Group penalties by pillar
        completeness_penalty = 0.0
        uniqueness_penalty = 0.0
        validity_penalty = 0.0
        consistency_penalty = 0.0

        for issue in issues:
            cat = issue.category
            ratio = issue.affected_ratio

            if cat == "missing":
                # Missing cells proportion relative to total cells
                cell_ratio = issue.affected_count / total_cells
                completeness_penalty += min(cell_ratio * 100.0 * 1.5, 50.0)
            elif cat == "empty_col":
                # Each completely empty column represents a structural defect
                completeness_penalty += min((issue.affected_count / total_cols) * 60.0, 50.0)
            elif cat == "empty_row":
                completeness_penalty += min(ratio * 70.0, 50.0)

            elif cat == "duplicates":
                # Duplicate rows directly reduce uniqueness
                uniqueness_penalty += min(ratio * 100.0 * 1.2, 90.0)
            elif cat == "headers":
                # Duplicate headers are a critical uniqueness issue
                uniqueness_penalty += 30.0

            elif cat == "types":
                # Numbers stored as string or uncoercible types
                validity_penalty += min(ratio * 50.0, 40.0)
            elif cat == "dates":
                validity_penalty += min(ratio * 50.0, 40.0)
            elif cat == "outliers":
                # Outliers reduce validity modestly
                validity_penalty += min(ratio * 20.0, 20.0)

            elif cat == "whitespace" or cat == "casing":
                consistency_penalty += min(ratio * 30.0, 35.0)
            elif cat == "categories":
                consistency_penalty += min(ratio * 40.0, 30.0)

        # Cap pillar scores between 0 and 100
        comp_score = max(0.0, min(100.0, 100.0 - completeness_penalty))
        uniq_score = max(0.0, min(100.0, 100.0 - uniqueness_penalty))
        val_score = max(0.0, min(100.0, 100.0 - validity_penalty))
        cons_score = max(0.0, min(100.0, 100.0 - consistency_penalty))

        # Weighted composite score
        w_comp = config.weight_completeness
        w_uniq = config.weight_uniqueness
        w_val = config.weight_validity
        w_cons = config.weight_consistency
        total_w = w_comp + w_uniq + w_val + w_cons

        overall = (
            (comp_score * w_comp) + (uniq_score * w_uniq) + (val_score * w_val) + (cons_score * w_cons)
        ) / total_w

        return QualityScoreBreakdown(
            overall_score=round(max(0.0, min(100.0, overall)), 1),
            completeness=round(comp_score, 1),
            uniqueness=round(uniq_score, 1),
            validity=round(val_score, 1),
            consistency=round(cons_score, 1),
            completeness_penalty=round(completeness_penalty, 1),
            uniqueness_penalty=round(uniqueness_penalty, 1),
            validity_penalty=round(validity_penalty, 1),
            consistency_penalty=round(consistency_penalty, 1),
        )
