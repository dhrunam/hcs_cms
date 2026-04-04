import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { ChatReadStateService, ChatRoleScope } from '../../services/chat/chat-read-state.service';
import { ChatMessageItem, ChatService } from '../../services/chat/chat.service';

@Component({
  selector: 'app-efiling-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './efiling-chat.html',
  styleUrl: './efiling-chat.css',
})
export class EfilingChatComponent implements OnChanges {
  @Input({ required: true }) filingId: number | null = null;
  @Input() composerTitle = 'Message';
  @Input({ required: true }) roleScope: ChatRoleScope = 'advocate';

  messages: ChatMessageItem[] = [];
  draftMessage = '';
  isLoading = false;
  isSending = false;
  errorMessage = '';

  constructor(
    private chatService: ChatService,
    private chatReadStateService: ChatReadStateService,
  ) {}

  ngOnChanges(changes: SimpleChanges): void {
    if ('filingId' in changes && this.filingId) {
      this.loadMessages();
    }
  }

  loadMessages(): void {
    if (!this.filingId) {
      this.messages = [];
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.chatService
      .getMessages(this.filingId)
      .pipe(finalize(() => (this.isLoading = false)))
      .subscribe({
        next: (messages) => {
          this.messages = Array.isArray(messages) ? messages : [];
          this.markLatestMessageAsSeen();
        },
        error: () => {
          this.errorMessage = 'Unable to load conversation right now.';
          this.messages = [];
        },
      });
  }

  sendMessage(): void {
    const message = this.draftMessage.trim();
    if (!this.filingId || !message || this.isSending) {
      return;
    }

    this.isSending = true;
    this.errorMessage = '';
    this.chatService
      .sendMessage(this.filingId, message)
      .pipe(finalize(() => (this.isSending = false)))
      .subscribe({
        next: (createdMessage) => {
          this.messages = [...this.messages, createdMessage];
          this.draftMessage = '';
          this.markLatestMessageAsSeen();
        },
        error: () => {
          this.errorMessage = 'Unable to send the message.';
        },
      });
  }

  getRoleLabel(message: ChatMessageItem): string {
    if (message.sender_role === 'advocate') {
      return 'Advocate';
    }
    if (message.sender_role === 'scrutiny_officer') {
      return 'Scrutiny Officer';
    }
    if (message.sender_role === 'system') {
      return 'System';
    }
    return 'User';
  }

  isAdvocateMessage(message: ChatMessageItem): boolean {
    return message.sender_role === 'advocate';
  }

  isScrutinyMessage(message: ChatMessageItem): boolean {
    return message.sender_role === 'scrutiny_officer';
  }

  private markLatestMessageAsSeen(): void {
    if (!this.filingId || this.messages.length === 0) {
      return;
    }
    const latestMessage = this.messages[this.messages.length - 1];
    if (!latestMessage?.id) {
      return;
    }
    this.chatReadStateService.markSeen(this.filingId, this.roleScope, latestMessage.id);
  }
}