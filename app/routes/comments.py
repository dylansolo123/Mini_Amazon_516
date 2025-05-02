from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from ..models.comment import Comment

bp = Blueprint('comments', __name__)

@bp.route('/api/comments/create', methods=['POST'])
@login_required
def create_comment():
    data = request.get_json()
    review_id = data.get('review_id')
    comment_text = data.get('comment_text')
    
    if not review_id or not comment_text:
        return jsonify({'error': 'Missing required fields'}), 400
        
    comment, message = Comment.create(review_id, current_user.id, comment_text)
    if comment:
        return jsonify({
            'success': True,
            'message': message,
            'comment': {
                'id': comment.comment_id,
                'text': comment.comment_text,
                'points': comment.points,
                'created_at': comment.created_at.isoformat(),
                'user_name': current_user.full_name
            }
        })
    return jsonify({'error': message}), 400

@bp.route('/api/comments/<int:comment_id>/vote', methods=['POST'])
@login_required
def vote_comment(comment_id):
    data = request.get_json()
    vote_value = data.get('vote_value')
    
    if vote_value not in [-1, 1]:
        return jsonify({'error': 'Invalid vote value'}), 400
        
    success, message = Comment.vote(comment_id, current_user.id, vote_value)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'error': message}), 400

@bp.route('/api/comments/<int:comment_id>/remove-vote', methods=['POST'])
@login_required
def remove_vote(comment_id):
    success, message = Comment.remove_vote(comment_id, current_user.id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'error': message}), 400

@bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    success, message = Comment.delete(comment_id, current_user.id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'error': message}), 400 