import { checkThatNavBarExists } from "./utils";

describe("E2E Tests", () => {
    it('can view cards', () => {
        cy.visit('/')
        cy.contains(/quantinuum's qccd ion-trap hardware, the world's highest peforming quantum computer./i)
        cy.contains(/cloud platform connecting users with hardware and compilation services, alongside associated data./i)
        cy.contains(/quantum computing toolkit and optimizing compiler/i)
        cy.contains(/platform for complex molecular and materials simulations/i)
        cy.contains(/python toolkit for quantum natural language processing/i)
    })

    it('test h-series link', {
        retries: {
            runMode: 20,
            openMode: 20
        }
    }, () => {
        cy.visit('/')
        cy.get('a[href=h-series]').should('be.visible').click()
        cy.contains(/the world's highest-performing quantum hardware/i)
    })

    it('test nexus link', {
        retries: {
            runMode: 20,
            openMode: 20
        }
    }, () => {
        cy.visit('/')
        cy.get('a[href=nexus]').should('be.visible').click()
        cy.contains(/the full stack quantum computing platform/i)
    })

    it('test tket link', {
        retries: {
            runMode: 20,
            openMode: 20
        }
    }, () => {
        cy.visit('/')
        cy.get('a[href=tket]').should('be.visible').click()
        cy.contains(/the universal quantum toolkit/i)
    })

    it('test inquanto link', {
        retries: {
            runMode: 20,
            openMode: 20
        }
    }, () => {
        cy.visit('/')
        cy.get('a[href=inquanto]').should('be.visible').click()
        cy.contains(/quantum chemistry on quantum computers/i)
    })

    it('test lambeq link', {
        retries: {
            runMode: 20,
            openMode: 20
        }
    }, () => {
        cy.visit('/')
        cy.get('a[href=lambeq]').should('be.visible').click()
        cy.contains(/natural language processing on quantum computers/i)
    })
})

